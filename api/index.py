from app import app
from flask import send_from_directory
import os

# Serve static files from the root
@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return app.handle_user_exception(Exception("Not Found"))

# This is needed for Vercel
application = app
