#!/bin/bash

# Afficher les variables d'environnement pour le débogage
echo "=== Variables d'environnement ==="
echo "PYTHON_VERSION: $(python --version)"
echo "PIP_VERSION: $(pip --version)"
echo "FLASK_ENV: $FLASK_ENV"
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."  # Affiche uniquement les 30 premiers caractères

# Installer les dépendances
echo "=== Installation des dépendances ==="
pip install -r requirements.txt

# Créer le répertoire api s'il n'existe pas
mkdir -p api

# Copier les fichiers nécessaires dans le répertoire api
echo "=== Copie des fichiers pour Vercel ==="
cp app.py api/
cp -r templates/ api/ 2>/dev/null || true
cp -r static/ api/ 2>/dev/null || true

# Donner les permissions d'exécution
chmod +x vercel-build.sh

echo "=== Build terminé avec succès ==="
