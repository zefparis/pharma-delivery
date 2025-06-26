"""
Point d'entrée pour l'initialisation de la base de données via une requête HTTP.
Ce fichier est utilisé par Vercel pour initialiser la base de données.
"""

import os
import sys
import json
import logging
import traceback
import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer l'application Flask
from app import create_app, db

# Créer l'application avec la configuration de production
app = create_app({
    'FLASK_ENV': 'production',
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'pharma-express-secret-key-2024'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'require',
            'application_name': 'pharma_delivery_setup_db',
            'options': '-c statement_timeout=60000'  # 60 secondes de timeout
        }
    }
})

class handler(BaseHTTPRequestHandler):
    """Gestionnaire de requêtes HTTP pour l'initialisation de la base de données."""
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Définit les en-têtes de la réponse HTTP."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """Envoie une réponse JSON."""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Gère les requêtes OPTIONS pour CORS."""
        self._set_headers(200)
    
    def do_GET(self):
        """Gère les requêtes GET pour initialiser la base de données."""
        try:
            # Journaliser la requête entrante
            logger.info(f"Requête reçue: {self.command} {self.path}")
            
            # Vérifier si c'est une requête de vérification de santé
            if self.path == '/health':
                self._send_json_response({
                    'status': 'ok',
                    'message': 'Service en cours d\'exécution',
                    'timestamp': datetime.datetime.utcnow().isoformat()
                })
                return
            
            # Vérifier si l'URL contient un token d'autorisation
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Vérifier le token d'autorisation (optionnel mais recommandé)
            auth_token = query_params.get('token', [None])[0]
            expected_token = os.environ.get('SETUP_DB_TOKEN')
            
            if expected_token and auth_token != expected_token:
                logger.warning("Tentative non autorisée d'accès à l'initialisation de la base de données")
                self._send_json_response({
                    'status': 'error',
                    'message': 'Non autorisé',
                    'error': 'Token d\'autorisation manquant ou invalide'
                }, 403)
                return
            
            with app.app_context():
                try:
                    logger.info("Début de l'initialisation de la base de données...")
                    
                    # Créer toutes les tables
                    db.create_all()
                    
                    # Vérifier si les tables ont été créées
                    from sqlalchemy import inspect
                    inspector = inspect(db.engine)
                    tables = inspector.get_table_names()
                    
                    logger.info(f"Base de données initialisée avec succès. Tables créées: {tables}")
                    
                    self._send_json_response({
                        'status': 'success',
                        'tables_created': tables,
                        'message': 'Base de données initialisée avec succès!',
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    error_msg = f"Erreur lors de l'initialisation de la base de données: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    
                    self._send_json_response({
                        'status': 'error',
                        'message': 'Erreur lors de l\'initialisation de la base de données',
                        'error': str(e) if app.config.get('DEBUG') else 'Erreur interne du serveur',
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    }, 500)
                    
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Essayer d'envoyer une réponse d'erreur même si quelque chose s'est mal passé
            try:
                self._send_json_response({
                    'status': 'error',
                    'message': 'Erreur inattendue',
                    'error': str(e) if app.config.get('DEBUG') else 'Une erreur inattendue est survenue',
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }, 500)
            except:
                # Si nous ne pouvons pas envoyer de réponse, nous ne pouvons rien faire de plus
                pass
