from app import db
from models import Product, User

def init_mock_data():
    """Initialize the database with mock data if it's empty"""
    
    # Only add data if no products exist
    if Product.query.count() > 0:
        return
    
    # Sample medications data
    medications = [
        {
            'name': 'Paracétamol 500mg',
            'description': 'Antalgique et antipyrétique pour soulager la douleur et la fièvre.',
            'price': 2500,
            'category': 'Antalgiques',
            'manufacturer': 'Pharma Congo',
            'stock_quantity': 100,
            'image_url': 'https://via.placeholder.com/300x300/007bff/ffffff?text=Paracétamol',
            'prescription_required': False,
            'active_ingredient': 'Paracétamol',
            'dosage': '500mg',
            'featured': True
        },
        {
            'name': 'Amoxicilline 250mg',
            'description': 'Antibiotique à large spectre pour traiter diverses infections bactériennes.',
            'price': 8500,
            'category': 'Antibiotiques',
            'manufacturer': 'MediKin',
            'stock_quantity': 75,
            'image_url': 'https://via.placeholder.com/300x300/28a745/ffffff?text=Amoxicilline',
            'prescription_required': True,
            'active_ingredient': 'Amoxicilline',
            'dosage': '250mg',
            'featured': True
        },
        {
            'name': 'Vitamine C 1000mg',
            'description': 'Complément vitaminique pour renforcer le système immunitaire.',
            'price': 5000,
            'category': 'Vitamines',
            'manufacturer': 'VitaHealth',
            'stock_quantity': 120,
            'image_url': 'https://via.placeholder.com/300x300/ffc107/000000?text=Vitamine+C',
            'prescription_required': False,
            'active_ingredient': 'Acide ascorbique',
            'dosage': '1000mg',
            'featured': True
        },
        {
            'name': 'Ibuprofène 400mg',
            'description': 'Anti-inflammatoire non stéroïdien pour douleurs et inflammations.',
            'price': 3500,
            'category': 'Anti-inflammatoires',
            'manufacturer': 'Pharma Congo',
            'stock_quantity': 90,
            'image_url': 'https://via.placeholder.com/300x300/dc3545/ffffff?text=Ibuprofène',
            'prescription_required': False,
            'active_ingredient': 'Ibuprofène',
            'dosage': '400mg',
            'featured': True
        },
        {
            'name': 'Oméprazole 20mg',
            'description': 'Inhibiteur de la pompe à protons pour traiter les ulcères gastriques.',
            'price': 6500,
            'category': 'Gastroentérologie',
            'manufacturer': 'MediKin',
            'stock_quantity': 60,
            'image_url': 'https://via.placeholder.com/300x300/6c757d/ffffff?text=Oméprazole',
            'prescription_required': True,
            'active_ingredient': 'Oméprazole',
            'dosage': '20mg',
            'featured': False
        },
        {
            'name': 'Aspirine 100mg',
            'description': 'Antiagrégant plaquettaire pour prévention cardiovasculaire.',
            'price': 2000,
            'category': 'Cardiologie',
            'manufacturer': 'CardioMed',
            'stock_quantity': 80,
            'image_url': 'https://via.placeholder.com/300x300/17a2b8/ffffff?text=Aspirine',
            'prescription_required': False,
            'active_ingredient': 'Acide acétylsalicylique',
            'dosage': '100mg',
            'featured': False
        },
        {
            'name': 'Métronidazole 250mg',
            'description': 'Antibiotique et antiparasitaire pour infections anaérobies.',
            'price': 4500,
            'category': 'Antibiotiques',
            'manufacturer': 'Pharma Congo',
            'stock_quantity': 55,
            'image_url': 'https://via.placeholder.com/300x300/6f42c1/ffffff?text=Métronidazole',
            'prescription_required': True,
            'active_ingredient': 'Métronidazole',
            'dosage': '250mg',
            'featured': False
        },
        {
            'name': 'Loratadine 10mg',
            'description': 'Antihistaminique pour traiter les allergies et rhinites.',
            'price': 3000,
            'category': 'Allergologie',
            'manufacturer': 'AllergoKin',
            'stock_quantity': 70,
            'image_url': 'https://via.placeholder.com/300x300/fd7e14/ffffff?text=Loratadine',
            'prescription_required': False,
            'active_ingredient': 'Loratadine',
            'dosage': '10mg',
            'featured': True
        },
        {
            'name': 'Zinc 15mg',
            'description': 'Complément minéral essentiel pour le système immunitaire.',
            'price': 4000,
            'category': 'Vitamines',
            'manufacturer': 'VitaHealth',
            'stock_quantity': 100,
            'image_url': 'https://via.placeholder.com/300x300/e83e8c/ffffff?text=Zinc',
            'prescription_required': False,
            'active_ingredient': 'Sulfate de zinc',
            'dosage': '15mg',
            'featured': False
        },
        {
            'name': 'Salbutamol 100mcg',
            'description': 'Bronchodilatateur en inhalation pour traitement de l\'asthme.',
            'price': 12000,
            'category': 'Pneumologie',
            'manufacturer': 'RespiroMed',
            'stock_quantity': 40,
            'image_url': 'https://via.placeholder.com/300x300/20c997/ffffff?text=Salbutamol',
            'prescription_required': True,
            'active_ingredient': 'Salbutamol',
            'dosage': '100mcg/dose',
            'featured': True
        },
        {
            'name': 'Fer + Acide Folique',
            'description': 'Complément pour traiter et prévenir l\'anémie ferriprive.',
            'price': 3500,
            'category': 'Vitamines',
            'manufacturer': 'FerroHealth',
            'stock_quantity': 85,
            'image_url': 'https://via.placeholder.com/300x300/795548/ffffff?text=Fer+Folique',
            'prescription_required': False,
            'active_ingredient': 'Sulfate ferreux + Acide folique',
            'dosage': '65mg + 400mcg',
            'featured': False
        },
        {
            'name': 'Ciprofloxacine 500mg',
            'description': 'Antibiotique fluoroquinolone pour infections sévères.',
            'price': 9500,
            'category': 'Antibiotiques',
            'manufacturer': 'MediKin',
            'stock_quantity': 35,
            'image_url': 'https://via.placeholder.com/300x300/343a40/ffffff?text=Ciprofloxacine',
            'prescription_required': True,
            'active_ingredient': 'Ciprofloxacine',
            'dosage': '500mg',
            'featured': False
        }
    ]
    
    # Add products to database
    for med_data in medications:
        product = Product(**med_data)
        db.session.add(product)
    
    # Create admin user if no users exist
    if User.query.count() == 0:
        admin_user = User(
            email='admin@kinpharma.cd',
            first_name='Admin',
            last_name='KinPharma',
            phone='+243123456789',
            address='Kinshasa, RDC',
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
    
    db.session.commit()
    print("Mock data initialized successfully!")
