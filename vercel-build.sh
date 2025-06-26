#!/bin/bash

# =============================================================================
# Script de build pour le déploiement Vercel de l'application PharmaDelivery
# =============================================================================

# Configuration
set -euo pipefail  # Mode strict: arrête le script en cas d'erreur
IFS=$'\n\t'       # Définit le séparateur de champ pour éviter les problèmes d'espaces

# Fonction pour afficher un message d'en-tête
section() {
    echo -e "\n\033[1;34m=== $1 ===\033[0m"
}

# Fonction pour afficher un message de succès
success() {
    echo -e "\033[1;32m✓ $1\033[0m"
}

# Fonction pour afficher un message d'erreur et quitter
error_exit() {
    echo -e "\033[1;31m✗ ERREUR: $1\033[0m" >&2
    exit 1
}

# =============================================================================
# Début du script
# =============================================================================
section "Démarrage du processus de build"

# Vérification des prérequis
section "Vérification des prérequis"
command -v python3 >/dev/null 2>&1 || error_exit "Python 3 n'est pas installé"
command -v pip3 >/dev/null 2>&1 || error_exit "pip3 n'est pas installé"

# Affichage des versions
section "Versions des outils"
echo "Système: $(uname -a)"
python3 --version
pip3 --version

# Affichage des variables d'environnement (sans les valeurs sensibles)
section "Variables d'environnement"
printenv | grep -v -iE 'SECRET|PASSWORD|TOKEN|KEY|DATABASE_URL|SUPABASE|PRIVATE' | sort

# Vérification des variables d'environnement requises
section "Vérification des variables d'environnement"
REQUIRED_ENV_VARS=(
    "DATABASE_URL"
    "SECRET_KEY"
    "SUPABASE_URL"
    "SUPABASE_KEY"
)

for var in "${REQUIRED_ENV_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "⚠️  \033[33mAttention: $var n'est pas défini\033[0m"
    else
        echo -e "✓ $var est défini"
    fi
done

# Installation des dépendances système
section "Installation des dépendances système"
if command -v apt-get > /dev/null; then
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        libwebp-dev \
        libmagic1 \
        && rm -rf /var/lib/apt/lists/*
    success "Dépendances système installées"
else
    echo "Gestionnaire de paquets apt non trouvé, poursuite sans installation de dépendances système"
fi

# Mise à jour de pip et installation des dépendances Python
section "Installation des dépendances Python"
python3 -m pip install --upgrade pip setuptools wheel
pip3 install --no-cache-dir -r requirements.txt

# Vérification de l'installation des dépendances
section "Vérification des dépendances Python"
REQUIRED_PACKAGES=(
    "Flask"
    "SQLAlchemy"
    "psycopg2-binary"
    "Flask-SQLAlchemy"
    "python-dotenv"
    "gunicorn"
)

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip3 list --format=columns | grep -q "^$pkg "; then
        echo -e "⚠️  \033[33mAttention: $pkg n'est pas installé\033[0m"
    else
        echo -e "✓ $pkg est installé"
    fi
done

# Configuration des répertoires
section "Configuration des répertoires"
REQUIRED_DIRS=(
    "api"
    "static"
    "templates"
    "migrations"
    "logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    mkdir -p "$dir"
    chmod -R 755 "$dir"
    echo "✓ Répertoire configuré: $dir"
done

# Copie des fichiers nécessaires
section "Préparation des fichiers pour le déploiement"
FILES_TO_COPY=(
    "app.py"
    "config.py"
    "*.py"
    "requirements.txt"
    ".env"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -e "$file" ]; then
        cp -r "$file" api/ 2>/dev/null || true
        echo "✓ Fichier copié: $file"
    fi
done

# Création des fichiers manquants
section "Création des fichiers manquants"

# Fichier __init__.py pour le package api
cat > api/__init__.py << 'EOL'
"""
Package principal de l'API PharmaDelivery.
Ce fichier est nécessaire pour que Python traite le répertoire comme un package.
"""
__version__ = '1.0.0'
EOL

# Fichier de log si inexistant
if [ ! -f "logs/app.log" ]; then
    mkdir -p logs
    touch logs/app.log
    chmod 666 logs/app.log
    echo "✓ Fichier de log créé: logs/app.log"
fi

# Vérification de la connexion à la base de données
section "Test de connexion à la base de données"

if [ -n "${DATABASE_URL:-}" ]; then
    # Normalisation de l'URL de la base de données
    if [[ "$DATABASE_URL" == postgres://* ]]; then
        echo "Conversion de l'URL de la base de données de postgres:// à postgresql://"
        export DATABASE_URL="postgresql://${DATABASE_URL#postgres://}"
    fi
    
    # Masquage des informations sensibles dans les logs
    DB_MASKED_URL=$(echo "$DATABASE_URL" | sed -E 's/([^:]+:)[^:]+@/\1********@/g')
    echo "Tentative de connexion à la base de données: ${DB_MASKED_URL}"
    
    # Test de connexion avec Python
    if python3 -c "
import os
import sys
import psycopg2
from urllib.parse import urlparse
from contextlib import contextmanager

@contextmanager
def connect_db():
    conn = None
    try:
        conn = psycopg2.connect(
            os.environ['DATABASE_URL'],
            connect_timeout=10,
            sslmode='require',
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        yield conn
    except Exception as e:
        print(f"Erreur de connexion: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()

try:
    # Test de requête simple
    with connect_db() as conn:
        with conn.cursor() as cur:
            # Test de requête simple
            cur.execute('SELECT version()')
            db_version = cur.fetchone()[0]
            print(f"✓ Connecté à PostgreSQL: {db_version.split(',')[0]}")
            
            # Vérification des tables nécessaires
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"✓ Tables disponibles: {len(tables)}")
            
except Exception as e:
    print(f"Erreur lors de la vérification de la base de données: {e}", file=sys.stderr)
    sys.exit(1)
"; then
        success "Test de connexion à la base de données réussi"
    else
        error_exit "Échec du test de connexion à la base de données"
    fi
else
    echo -e "⚠️  \033[33mAvertissement: Aucune URL de base de données trouvée. Le test de connexion est ignoré.\033[0m"
fi

# Nettoyage
section "Nettoyage"
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo "✓ Cache Python nettoyé"
fi

if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    echo "✓ Cache pytest nettoyé"
fi

# Vérification finale
section "Vérification finale"
REQUIRED_API_FILES=(
    "api/__init__.py"
    "api/index.py"
    "app.py"
    "config.py"
)

for file in "${REQUIRED_API_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "✓ Fichier présent: $file"
    else
        echo -e "⚠️  \033[33mFichier manquant: $file\033[0m"
    fi
done

# Vérification de l'import de l'application
section "Vérification de l'import de l'application"
if python3 -c "
import sys
import os

# Ajout du répertoire courant au chemin Python
sys.path.append(os.getcwd())

try:
    # Essayer d'importer l'application
    from api.index import app
    print('✓ Import de api.index réussi')
    
    # Vérifier que l'application a été créée avec succès
    if hasattr(app, 'config'):
        print(f'✓ Configuration chargée (ENV: {app.config.get(\"FLASK_ENV\", \"non défini\")})')
    else:
        print('⚠️  La configuration de l\'application semble incomplète')
        sys.exit(1)
        
except ImportError as e:
    print(f'❌ Erreur d\'import: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print(f'❌ Erreur inattendue: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"; then
    success "Vérification de l'application réussie"
else
    error_exit "Échec de la vérification de l'application"
fi

# Affichage de l'espace disque
echo -e "\n\033[1mUtilisation du disque:\033[0m"
df -h .

# Message de fin
section "Construction terminée avec succès"
echo "L'application est prête pour le déploiement sur Vercel"
echo "Date: $(date)"

exit 0
