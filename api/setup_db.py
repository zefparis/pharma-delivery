import os
import sys
from http.server import BaseHTTPRequestHandler
import json
from app import app, db

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with app.app_context():
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                try:
                    # Créer les tables
                    db.create_all()
                    
                    # Vérifier si les tables existent
                    from sqlalchemy import inspect
                    inspector = inspect(db.engine)
                    tables = inspector.get_table_names()
                    
                    response = {
                        'status': 'success',
                        'tables_created': tables,
                        'message': 'Base de données initialisée avec succès!'
                    }
                    self.wfile.write(json.dumps(response).encode())
                    
                except Exception as e:
                    error_msg = f"Erreur lors de l'initialisation de la base de données: {str(e)}"
                    print(error_msg)
                    self.send_response(500)
                    self.wfile.write(json.dumps({
                        'status': 'error',
                        'message': error_msg
                    }).encode())
                    
        except Exception as e:
            self.send_response(500)
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': f"Erreur inattendue: {str(e)}"
            }).encode())
