import os
import sys
from app import app, db
from models import *

def init_db():
    with app.app_context():
        print("Création des tables de la base de données...")
        try:
            db.create_all()
            print("Tables créées avec succès!")
            return True
        except Exception as e:
            print(f"Erreur lors de la création des tables: {str(e)}")
            return False

if __name__ == "__main__":
    print("Démarrage de l'initialisation de la base de données...")
    if init_db():
        print("Base de données initialisée avec succès!")
        sys.exit(0)
    else:
        print("Échec de l'initialisation de la base de données")
        sys.exit(1)
