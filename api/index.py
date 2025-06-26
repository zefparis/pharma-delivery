import os
import sys
import logging
import traceback
from app import app
from flask import jsonify, send_from_directory, request

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.info("Chargement du point d'entrée API")

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestion des erreurs
@app.errorhandler(500)
def internal_error(error):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_details = {
        'error': str(error),
        'type': str(exc_type),
        'message': str(exc_value),
        'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
    }
    logger.error("Erreur 500: %s", error_details, exc_info=True)
    return jsonify({"error": "Erreur interne du serveur", "details": str(error)}), 500

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
    try:
        logger.info("Démarrage du serveur de développement")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error("Erreur au démarrage: %s", str(e), exc_info=True)
        raise
