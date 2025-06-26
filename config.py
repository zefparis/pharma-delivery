"""
Configuration de l'application.
Ce fichier contient les paramètres de configuration pour différents environnements.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """Configuration de base commune à tous les environnements."""
    
    # Clé secrète pour les sessions et les tokens CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    
    # Configuration de la base de données
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration du serveur de messagerie
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuration de l'administrateur
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    
    # Nom de l'application
    APP_NAME = "PharmaDelivery"
    
    # Nombre d'éléments par page pour la pagination
    ITEMS_PER_PAGE = 20
    
    # Activer/désactiver le mode débogage
    DEBUG = False
    
    # Configuration CORS
    CORS_HEADERS = 'Content-Type'
    
    # Configuration de la sécurité
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-salt-123'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    
    # Configuration des sessions
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure en secondes


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data-dev.sqlite')
    
    # Désactiver la protection CSRF en développement pour faciliter les tests
    WTF_CSRF_ENABLED = False


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'  # Utilisation de la mémoire pour les tests
    WTF_CSRF_ENABLED = False  # Désactiver CSRF pour les tests


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    # Récupérer l'URL de la base de données depuis les variables d'environnement
    database_url = os.environ.get('DATABASE_URL', '')
    
    # Si l'URL commence par postgres://, la remplacer par postgresql://
    if database_url.startswith('postgres://'):
        database_url = 'postgresql://' + database_url[11:]
    
    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data.sqlite')
    
    # Forcer l'utilisation de HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Désactiver le mode débogage en production
    DEBUG = False
    
    # Configuration de la base de données pour la production
    SQLALCHEMY_ENGINE_OPTIONS = {
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
            'application_name': 'pharma_delivery_app',
            'options': '-c statement_timeout=30000'  # 30 secondes de timeout par défaut
        },
        'executemany_mode': 'batch',
        'echo': False,
        'echo_pool': False,
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_reset_on_return': 'rollback',
        'pool_use_lifo': True
    }


# Dictionnaire des configurations disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Configuration actuelle basée sur la variable d'environnement FLASK_ENV
env = os.environ.get('FLASK_ENV', 'development').lower()
current_config = config.get(env, config['default'])
