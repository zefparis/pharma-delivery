import os
import logging
from app import app
from flask import jsonify, send_from_directory

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestion des erreurs
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur 500: {str(error)}", exc_info=True)
    return jsonify({"error": "Erreur interne du serveur"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

# Serveur de fichiers statiques
@app.route('/<path:path>')
def serve_static(path):
    try:
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return app.handle_user_exception(Exception("Not Found"))
    except Exception as e:
        logger.error(f"Erreur serveur statique: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint de test
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

# Ceci est nécessaire pour Vercel
application = app

# Log de démarrage
if __name__ == "__main__":
    logger.info("Démarrage de l'application Flask")
    app.run(debug=True)
