"""
Point d'entrée WSGI pour le déploiement sur Vercel.
Ce fichier est utilisé par Gunicorn et d'autres serveurs WSGI.
"""

import os
import sys
import logging

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Créer l'application
from app import create_app

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
            'sslmode': 'require'
        }
    }
})

# Ceci est nécessaire pour Vercel
application = app

if __name__ == "__main__":
    # Ce bloc ne sera exécuté que lors d'un lancement local avec python wsgi.py
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Démarrage du serveur sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
