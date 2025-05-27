import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pharma-express-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pharma-express.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

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
    admin = User.query.filter_by(email='admin@kinpharma.cd').first()
    if not admin:
        admin = User(
            email='admin@kinpharma.cd',
            name='Administrateur KinPharma',
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
