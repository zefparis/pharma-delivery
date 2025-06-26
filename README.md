# PharmaDelivery - Plateforme de Gestion Pharmaceutique

[![Déployer avec Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvotre-utilisateur%2Fpharmadelivery&env=DATABASE_URL,SECRET_KEY,SUPABASE_URL,SUPABASE_KEY&envDescription=Configuration%20requise%20pour%20PharmaDelivery&envLink=https%3A%2F%2Fgithub.com%2Fvotre-utilisateur%2Fpharmadelivery%2Fblob%2Fmain%2F.env.example&project-name=pharma-delivery&repository-name=pharma-delivery)

## 📋 Table des matières

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Configuration requise](#-configuration-requise)
- [Installation locale](#-installation-locale)
- [Déploiement sur Vercel](#-déploiement-sur-vercel)
- [Variables d'environnement](#-variables-denvironnement)
- [Structure du projet](#-structure-du-projet)
- [Développement](#-développement)
- [Tests](#-tests)
- [Sécurité](#-sécurité)
- [Licence](#-licence)

## 🚀 Présentation

PharmaDelivery est une application web complète de gestion pharmaceutique conçue pour les pharmacies et les points de vente de médicaments. Cette solution offre une gestion complète des stocks, des ventes, des fournisseurs et des clients, avec une interface intuitive et des fonctionnalités avancées.

## ✨ Fonctionnalités

- **Gestion des médicaments** : Ajout, modification et suivi des stocks
- **Gestion des ventes** : Enregistrement des transactions et facturation
- **Gestion des fournisseurs** : Suivi des commandes et des livraisons
- **Gestion des clients** : Fiches clients et historique d'achat
- **Rapports et statistiques** : Tableaux de bord et analyses
- **API RESTful** : Pour une intégration avec d'autres systèmes
- **Interface administrateur** : Gestion des utilisateurs et des paramètres

## 🖥️ Configuration requise

- Python 3.11+
- PostgreSQL 13+
- Node.js 16+ (pour les assets frontend)
- npm ou yarn

## 🛠️ Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/pharmadelivery.git
cd pharmadelivery
```

### 2. Créer un environnement virtuel

```bash
# Sur Windows
python -m venv venv
.\venv\Scripts\activate

# Sur macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet en vous basant sur `.env.example` :

```bash
cp .env.example .env
```

Puis éditez le fichier `.env` pour configurer votre application.

### 5. Initialiser la base de données

```bash
flask db upgrade
flask init-db
```

### 6. Lancer l'application en mode développement

```bash
flask run
```

L'application sera disponible à l'adresse : http://localhost:5000

## ☁️ Déploiement sur Vercel

### 1. Prérequis

- Un compte [Vercel](https://vercel.com/)
- Un compte [Supabase](https://supabase.com/) pour la base de données PostgreSQL
- Les variables d'environnement configurées dans Vercel

### 2. Déploiement automatique

[![Déployer avec Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvotre-utilisateur%2Fpharmadelivery&env=DATABASE_URL,SECRET_KEY,SUPABASE_URL,SUPABASE_KEY&envDescription=Configuration%20requise%20pour%20PharmaDelivery&envLink=https%3A%2F%2Fgithub.com%2Fvotre-utilisateur%2Fpharmadelivery%2Fblob%2Fmain%2F.env.example&project-name=pharma-delivery&repository-name=pharma-delivery)

### 3. Déploiement manuel

1. Poussez votre code sur un dépôt Git (GitHub, GitLab, Bitbucket)
2. Connectez votre dépôt à Vercel
3. Configurez les variables d'environnement dans les paramètres du projet Vercel
4. Déployez !

## 🔧 Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration de base
FLASK_ENV=development
DEBUG=False
SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée

# Base de données
DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/nom_de_la_base

# Supabase
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_clé_anonyme_supabase

# Configuration CORS
FRONTEND_URL=http://localhost:3000
```

Consultez le fichier `.env.example` pour une liste complète des variables disponibles.

## 📁 Structure du projet

```
pharma-delivery/
├── app/                      # Code source principal de l'application
│   ├── __init__.py           # Initialisation de l'application Flask
│   ├── models/               # Modèles de données SQLAlchemy
│   ├── routes/               # Routes de l'API
│   ├── services/             # Logique métier
│   ├── static/               # Fichiers statiques (CSS, JS, images)
│   └── templates/            # Templates Jinja2
├── migrations/               # Fichiers de migration de base de données
├── tests/                    # Tests unitaires et d'intégration
├── .env.example              # Exemple de fichier de configuration
├── .gitignore                # Fichiers à ignorer par Git
├── config.py                 # Configuration de l'application
├── requirements.txt          # Dépendances Python
├── runtime.txt               # Version de Python pour Vercel
└── vercel.json              # Configuration Vercel
```

## 🚀 Développement

### Lancer le serveur de développement

```bash
flask run --debug
```

### Créer une nouvelle migration de base de données

```bash
flask db migrate -m "Description des modifications"
flask db upgrade
```

### Formater le code

```bash
black .
flake8
```

## 🧪 Tests

### Lancer les tests

```bash
pytest
```

### Générer un rapport de couverture de code

```bash
pytest --cov=app tests/
```

## 🔒 Sécurité

### Signaler une vulnérabilité

Si vous découvrez une vulnérabilité de sécurité, merci de ne pas créer d'issue publique. Contactez-nous à l'adresse security@votredomaine.com pour signaler le problème.

### Bonnes pratiques

- Ne jamais commettre de données sensibles dans le code source
- Utiliser des variables d'environnement pour les informations sensibles
- Maintenir les dépendances à jour
- Utiliser HTTPS en production
- Implémenter une authentification forte

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Flask](https://flask.palletsprojects.com/) - Le framework web utilisé
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM pour Python
- [Vercel](https://vercel.com/) - Plateforme de déploiement
- [Supabase](https://supabase.com/) - Backend as a Service avec PostgreSQL

---

<div align="center">
  <sub>Développé avec ❤️ par votre équipe</sub>
</div>
