"""
Point d'entrée principal de l'application pour le déploiement sur Vercel.
Ce fichier est utilisé par Vercel pour servir l'application Flask.
"""

import os
import sys
import json
import logging
import traceback
import datetime
from functools import wraps
from flask import jsonify, send_from_directory, request, current_app

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

# Import de l'application Flask
from app import create_app, db

# Création de l'application avec la configuration appropriée
app = create_app({
    'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
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
            'application_name': 'pharma_delivery_api',
            'options': '-c statement_timeout=30000'  # 30 secondes de timeout
        },
        'executemany_mode': 'batch',
        'echo': False,
        'echo_pool': False,
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_reset_on_return': 'rollback',
        'pool_use_lifo': True
    }
})

# Middleware pour logger les requêtes entrantes
@app.before_request
def log_request():
    """Log les informations de la requête entrante."""
    if app.config.get('DEBUG'):
        # Ne pas logger les mots de passe
        log_data = {
            'method': request.method,
            'path': request.path,
            'args': dict(request.args),
            'headers': {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'cookie']}
        }
        
        if request.is_json:
            json_data = request.get_json(silent=True) or {}
            if 'password' in json_data:
                json_data = json_data.copy()
                json_data['password'] = '********'
            log_data['json'] = json_data
        elif request.form:
            form_data = dict(request.form)
            if 'password' in form_data:
                form_data = form_data.copy()
                form_data['password'] = '********'
            log_data['form'] = form_data
        
        logger.debug("Requête reçue: %s", json.dumps(log_data, indent=2, ensure_ascii=False))
    else:
        logger.info("Requête reçue: %s %s", request.method, request.path)

# Fonction pour gérer les erreurs de manière générique
def handle_error(error, status_code=500, include_stacktrace=True):
    """Gère les erreurs de manière générique.
    
    Args:
        error: L'exception qui a été levée
        status_code: Le code HTTP à retourner
        include_stacktrace: Si True, inclut la stack trace en mode debug
        
    Returns:
        tuple: Un tuple (response, status_code) pour Flask
    """
    error_message = str(error) if str(error) else 'Une erreur inconnue est survenue'
    error_id = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    
    # Journaliser l'erreur
    logger.error(
        "Erreur %d (ID: %s): %s\n%s",
        status_code,
        error_id,
        error_message,
        traceback.format_exc() if include_stacktrace else ""
    )
    
    # Créer la réponse d'erreur
    response = {
        'status': 'error',
        'error_id': error_id,
        'message': error_message,
        'code': status_code,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    # En développement, ajouter la stack trace
    if app.config.get('DEBUG') and include_stacktrace:
        response['traceback'] = traceback.format_exc().splitlines()
    
    return jsonify(response), status_code

# Gestion des erreurs 400 (Bad Request)
@app.errorhandler(400)
def bad_request_error(error):
    return handle_error(error, 400)

# Gestion des erreurs 401 (Unauthorized)
@app.errorhandler(401)
def unauthorized_error(error):
    return handle_error(error, 401)

# Gestion des erreurs 403 (Forbidden)
@app.errorhandler(403)
def forbidden_error(error):
    return handle_error(error, 403)

# Gestion des erreurs 404 (Not Found)
@app.errorhandler(404)
def not_found_error(error):
    return handle_error(error, 404)

# Gestion des erreurs 405 (Method Not Allowed)
@app.errorhandler(405)
def method_not_allowed_error(error):
    return handle_error(error, 405)

# Gestion des erreurs 429 (Too Many Requests)
@app.errorhandler(429)
def too_many_requests_error(error):
    return handle_error(error, 429)

# Gestion des erreurs 500 (Internal Server Error)
@app.errorhandler(500)
def internal_error(error):
    return handle_error(error, 500)

# Gestion des exceptions non capturées
@app.errorhandler(Exception)
def handle_unhandled_exception(error):
    return handle_error(error, 500)

# Route pour servir les fichiers statiques
@app.route('/<path:path>')
def serve_static(path):
    """Sert les fichiers statiques depuis le répertoire static."""
    try:
        if path.startswith('static/'):
            return send_from_directory('static', path[7:])
        
        # Vérifier si le fichier existe dans le répertoire static
        static_file = os.path.join('static', path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return send_from_directory('static', path)
        
        # Si le fichier n'existe pas, renvoyer une erreur 404
        return not_found_error(None)
    except Exception as e:
        return handle_error(e, 500)

# Health check endpoint
@app.route('/health')
def health_check():
    """Endpoint de vérification de l'état de santé de l'application."""
    try:
        # Vérifier la connexion à la base de données
        db_status = 'ok'
        db_version = None
        try:
            result = db.session.execute('SELECT version()').fetchone()
            if result:
                db_version = result[0]
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        # Vérifier l'espace disque
        import shutil
        import psutil
        
        disk_usage = {}
        cpu_usage = {}
        memory_usage = {}
        
        try:
            # Utilisation du disque
            total, used, free = shutil.disk_usage('/')
            disk_usage = {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': (used / total) * 100 if total > 0 else 0
            }
            
            # Utilisation du CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_usage = {
                'percent_used': cpu_percent,
                'count': psutil.cpu_count(),
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            # Utilisation de la mémoire
            memory = psutil.virtual_memory()
            memory_usage = {
                'total': memory.total,
                'available': memory.available,
                'percent_used': memory.percent,
                'used': memory.used,
                'free': memory.free
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques système: {str(e)}")
        
        # Vérifier les dépendances
        dependencies = {
            'python': {
                'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'executable': sys.executable
            },
            'flask': {
                'version': None,
                'installed': False
            },
            'sqlalchemy': {
                'version': None,
                'installed': False
            },
            'psycopg2': {
                'version': None,
                'installed': False
            }
        }
        
        try:
            import flask
            dependencies['flask']['version'] = flask.__version__
            dependencies['flask']['installed'] = True
        except ImportError:
            pass
            
        try:
            import sqlalchemy
            dependencies['sqlalchemy']['version'] = sqlalchemy.__version__
            dependencies['sqlalchemy']['installed'] = True
        except ImportError:
            pass
            
        try:
            import psycopg2
            dependencies['psycopg2']['version'] = psycopg2.__version__
            dependencies['psycopg2']['installed'] = True
        except ImportError:
            pass
        
        # Vérifier les variables d'environnement (sensibles masquées)
        env_vars = {}
        for key, value in os.environ.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'pass', 'token']):
                env_vars[key] = '********' if value else ''
            else:
                env_vars[key] = value
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'application': 'PharmaDelivery API',
            'version': '1.0.0',
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'debug': app.config.get('DEBUG', False),
            'database': {
                'status': db_status,
                'version': db_version,
                'url': '********' if 'DATABASE_URL' in os.environ else None
            },
            'system': {
                'platform': sys.platform,
                'disk_usage': disk_usage,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage
            },
            'dependencies': dependencies,
            'request': {
                'method': request.method,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': str(request.user_agent)
            }
        })
    except Exception as e:
        return handle_error(e, 500)

# Fonction principale pour démarrer l'application
def main():
    """Point d'entrée principal pour le démarrage de l'application."""
    # Charger les variables d'environnement depuis le fichier .env si présent
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Variables d'environnement chargées depuis .env")
    except ImportError:
        logger.warning("Le module python-dotenv n'est pas installé. Les variables d'environnement ne seront pas chargées depuis .env")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des variables d'environnement: {str(e)}")
    
    # Démarrer le serveur de développement si exécuté directement
    if __name__ == '__main__':
        logger.info("Démarrage de l'application en mode développement...")
        
        # Configuration du serveur
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', '1', 't', 'y', 'yes']
        
        # Afficher les informations de configuration
        logger.info("Configuration de l'application:")
        logger.info(f"- Hôte: {host}")
        logger.info(f"- Port: {port}")
        logger.info(f"- Mode debug: {debug}")
        logger.info(f"- Environnement: {app.config.get('FLASK_ENV', 'production')}")
        
        # Démarrer le serveur
        logger.info(f"Démarrage du serveur sur http://{host}:{port}")
        app.run(debug=debug, host=host, port=port)
    else:
        logger.info("Application chargée avec succès en mode production")

# Ceci est nécessaire pour Vercel
application = app

# Point d'entrée principal
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical("Erreur critique lors du démarrage de l'application: %s", str(e), exc_info=True)
        raise
