import os
import sys
import logging
from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException

# Import de la configuration
from config import config, current_config

# Configuration du logging avancé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.info("Démarrage de l'application Flask")

class Base(DeclarativeBase, UserMixin):
    """Classe de base pour les modèles SQLAlchemy avec support de Flask-Login"""
    pass

# Initialisation des extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app(config_name=None):
    """Crée et configure une instance de l'application Flask.
    
    Args:
        config_name (str, optional): Le nom de la configuration à charger. Par défaut, utilise FLASK_ENV ou 'development'.
        
    Returns:
        Flask: L'application Flask configurée.
    """
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Configuration de l'application
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Chargement de la configuration appropriée
    app.config.from_object(config[config_name])
    
    # Configuration du logging
    if app.config.get('DEBUG'):
        app.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
        logging.basicConfig(level=logging.INFO)
    
    logger.info(f"Configuration chargée: {config_name}")
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Configuration pour le reverse proxy (nécessaire pour Vercel)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # Nombre de proxies de confiance pour X-Forwarded-For
        x_proto=1,  # Nombre de proxies de confiance pour X-Forwarded-Proto
        x_host=1,   # Nombre de proxies de confiance pour X-Forwarded-Host
        x_port=1,   # Nombre de proxies de confiance pour X-Forwarded-Port
        x_prefix=1  # Nombre de proxies de confiance pour X-Forwarded-Prefix
    )
    
    # Enregistrement des blueprints
    from routes import init_routes
    init_routes(app)
    
    # Middleware pour le logging des requêtes
    @app.before_request
    def log_request_info():
        """Log les informations de la requête entrante."""
        if app.config.get('DEBUG'):
            logger.info(f"Requête: {request.method} {request.path}")
            logger.debug(f"Headers: {dict(request.headers)}")
            logger.debug(f"Args: {request.args}")
            
            # Ne pas logger les mots de passe
            if request.is_json:
                json_data = request.get_json(silent=True) or {}
                if 'password' in json_data:
                    json_data = json_data.copy()
                    json_data['password'] = '********'
                logger.debug(f"JSON: {json_data}")
            elif request.form:
                form_data = dict(request.form)
                if 'password' in form_data:
                    form_data = form_data.copy()
                    form_data['password'] = '********'
                logger.debug(f"Form: {form_data}")
    
    # Gestion des erreurs 400 (Bad Request)
    @app.errorhandler(400)
    def bad_request_error(e):
        """Gère les erreurs 400 (Bad Request)."""
        logger.warning(f"Bad Request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Requête incorrecte',
            'error': str(e) if app.config.get('DEBUG') else None
        }), 400
    
    # Gestion des erreurs 401 (Unauthorized)
    @app.errorhandler(401)
    def unauthorized_error(e):
        """Gère les erreurs 401 (Unauthorized)."""
        logger.warning(f"Unauthorized: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Non autorisé',
            'error': str(e) if app.config.get('DEBUG') else 'Authentification requise'
        }), 401
    
    # Gestion des erreurs 403 (Forbidden)
    @app.errorhandler(403)
    def forbidden_error(e):
        """Gère les erreurs 403 (Forbidden)."""
        logger.warning(f"Forbidden: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Accès refusé',
            'error': str(e) if app.config.get('DEBUG') else 'Vous n\'avez pas les droits nécessaires'
        }), 403
    
    # Gestion des erreurs 404 (Not Found)
    @app.errorhandler(404)
    def page_not_found(e):
        """Gère les erreurs 404 (Not Found)."""
        logger.warning(f"Page non trouvée: {request.path}")
        return jsonify({
            'status': 'error',
            'message': 'Page non trouvée',
            'error': str(e) if app.config.get('DEBUG') else None
        }), 404
    
    # Gestion des erreurs 405 (Method Not Allowed)
    @app.errorhandler(405)
    def method_not_allowed_error(e):
        """Gère les erreurs 405 (Method Not Allowed)."""
        logger.warning(f"Méthode non autorisée: {request.method} {request.path}")
        return jsonify({
            'status': 'error',
            'message': 'Méthode non autorisée',
            'error': str(e) if app.config.get('DEBUG') else None
        }), 405
    
    # Gestion des erreurs 500 (Internal Server Error)
    @app.errorhandler(500)
    def internal_server_error(e):
        """Gère les erreurs 500 (Internal Server Error)."""
        logger.error(f"Erreur interne du serveur: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur interne du serveur',
            'error': str(e) if app.config.get('DEBUG') else 'Une erreur est survenue'
        }), 500
    
    # Gestion des exceptions non capturées
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Gère les exceptions non capturées."""
        logger.error(f"Exception non gérée: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur inattendue',
            'error': str(e) if app.config.get('DEBUG') else 'Une erreur inattendue est survenue'
        }), 500
    
    # Commande CLI pour initialiser la base de données
    @app.cli.command('init-db')
    def init_db_command():
        """Initialise la base de données."""
        try:
            db.create_all()
            logger.info('Base de données initialisée avec succès')
            return 'Base de données initialisée avec succès'
        except Exception as e:
            error_msg = f'Erreur lors de l\'initialisation de la base de données: {str(e)}'
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise e
    
    logger.info('Application initialisée avec succès')
    return app

# Création de l'application
app = create_app()

# Middleware pour logger les requêtes
@app.before_request
def log_request_info():
    logger.info(f"Requête: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Args: {request.args}")
    logger.debug(f"Form: {request.form}")
    logger.debug(f"JSON: {request.get_json(silent=True)}")

# Configure the database
def get_database_uri():
    if 'DATABASE_URL' in os.environ:
        # Production - PostgreSQL (Supabase)
        db_url = os.environ['DATABASE_URL']
        # Ensure the URL starts with postgresql:// (not postgres://)
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    else:
        # Development - SQLite
        return "sqlite:///pharma-express.db"

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
}

# Configure SQLAlchemy to use NullPool in production
if os.environ.get('FLASK_ENV') == 'production':
    from sqlalchemy.pool import NullPool
    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["poolclass"] = NullPool

# initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create sample data
    from models import User, Product, Category
    from werkzeug.security import generate_password_hash
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@pharma-express.cd').first()
    if not admin:
        admin = User(
            email='admin@pharma-express.cd',
            name='Administrateur Pharma-Express',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
    
    # Create categories if not exist
    categories_data = [
        {'name': 'Antalgiques', 'description': 'Médicaments contre la douleur'},
        {'name': 'Antibiotiques', 'description': 'Médicaments contre les infections'},
        {'name': 'Vitamines', 'description': 'Compléments vitaminiques'},
        {'name': 'Digestifs', 'description': 'Médicaments pour la digestion'},
        {'name': 'Respiratoires', 'description': 'Médicaments pour les voies respiratoires'},
        {'name': 'Cardiovasculaires', 'description': 'Médicaments pour le cœur'},
    ]
    
    for cat_data in categories_data:
        existing_cat = Category.query.filter_by(name=cat_data['name']).first()
        if not existing_cat:
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()
    
    # Create sample products if not exist
    if Product.query.count() == 0:
        sample_products = [
            {
                'name': 'Paracétamol 500mg',
                'description': 'Antalgique et antipyrétique. Traitement symptomatique des douleurs légères à modérées.',
                'price': 2500.0,
                'category_id': 1,
                'stock_quantity': 100,
                'image_url': 'https://via.placeholder.com/300x200/4CAF50/white?text=Paracétamol',
                'laboratory': 'PharmaCongo',
                'dosage': '500mg',
                'form': 'Comprimés',
                'prescription_required': False
            },
            {
                'name': 'Amoxicilline 250mg',
                'description': 'Antibiotique de la famille des pénicillines. Traitement des infections bactériennes.',
                'price': 8500.0,
                'category_id': 2,
                'stock_quantity': 50,
                'image_url': 'https://via.placeholder.com/300x200/2196F3/white?text=Amoxicilline',
                'laboratory': 'MediKin',
                'dosage': '250mg',
                'form': 'Gélules',
                'prescription_required': True
            },
            {
                'name': 'Vitamine C 1000mg',
                'description': 'Complément vitaminique. Renforce le système immunitaire.',
                'price': 5000.0,
                'category_id': 3,
                'stock_quantity': 75,
                'image_url': 'https://via.placeholder.com/300x200/FF9800/white?text=Vitamine+C',
                'laboratory': 'VitaKin',
                'dosage': '1000mg',
                'form': 'Comprimés effervescents',
                'prescription_required': False
            },
            {
                'name': 'Smecta',
                'description': 'Traitement symptomatique des diarrhées aiguës et chroniques.',
                'price': 3500.0,
                'category_id': 4,
                'stock_quantity': 60,
                'image_url': 'https://via.placeholder.com/300x200/795548/white?text=Smecta',
                'laboratory': 'DigestPharma',
                'dosage': '3g',
                'form': 'Sachets',
                'prescription_required': False
            },
            {
                'name': 'Sirop contre la toux',
                'description': 'Sirop expectorant pour le traitement de la toux grasse.',
                'price': 4500.0,
                'category_id': 5,
                'stock_quantity': 40,
                'image_url': 'https://via.placeholder.com/300x200/9C27B0/white?text=Sirop+Toux',
                'laboratory': 'RespirKin',
                'dosage': '15ml',
                'form': 'Sirop',
                'prescription_required': False
            },
            {
                'name': 'Aspirine Cardio 100mg',
                'description': 'Prévention des accidents cardiovasculaires.',
                'price': 6500.0,
                'category_id': 6,
                'stock_quantity': 30,
                'image_url': 'https://via.placeholder.com/300x200/F44336/white?text=Aspirine+Cardio',
                'laboratory': 'CardioKin',
                'dosage': '100mg',
                'form': 'Comprimés gastro-résistants',
                'prescription_required': True
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()

# Import routes
import routes
import admin_routes

# Configure static folder for Vercel
app.static_folder = 'static'

if __name__ == "__main__":
    app.run(debug=True)

# Gestion des erreurs HTTP
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    logger.error(f"HTTP Error: {e.code} - {e.name}")
    return jsonify({
        "error": e.name,
        "code": e.code,
        "description": e.description
    }), e.code

# Gestion des autres exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

# This is needed for Vercel
app = app
