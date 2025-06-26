# Guide de contribution pour PharmaDelivery

Merci de votre intérêt pour contribuer à PharmaDelivery ! Nous apprécions votre temps et vos efforts pour améliorer ce projet. Ce document vous guidera à travers le processus de contribution.

## 📋 Table des matières

- [Code de conduite](#-code-de-conduite)
- [Comment contribuer](#-comment-contribuer)
- [Configuration de l'environnement de développement](#-configuration-de-lenvironnement-de-développement)
- [Structure du projet](#-structure-du-projet)
- [Bonnes pratiques de codage](#-bonnes-pratiques-de-codage)
- [Tests](#-tests)
- [Soumission de modifications](#-soumission-de-modifications)
- [Signaler des bogues](#-signaler-des-bogues)
- [Proposer des fonctionnalités](#-proposer-des-fonctionnalités)
- [Revue de code](#-revue-de-code)
- [Questions](#-questions)

## ✨ Code de conduite

Ce projet et toutes les personnes qui y participent sont régis par notre [Code de Conduite](CODE_OF_CONDUCT.md). En participant, vous êtes tenu de respecter ce code. Merci de signaler tout comportement inacceptable à [votre-email@exemple.com](mailto:votre-email@exemple.com).

## 🚀 Comment contribuer

### Configuration de l'environnement de développement

1. **Fork** le dépôt sur GitHub.
2. **Clone** votre fork localement :
   ```bash
   git clone https://github.com/votre-utilisateur/pharmadelivery.git
   cd pharmadelivery
   ```
3. **Configurez** votre environnement :
   ```bash
   # Créez un environnement virtuel
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   
   # Installez les dépendances
   pip install -r requirements-dev.txt
   ```
4. **Configurez** les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditez .env avec vos paramètres
   ```
5. **Initialisez** la base de données :
   ```bash
   flask db upgrade
   flask init-db
   ```
6. **Lancez** l'application :
   ```bash
   flask run
   ```

## 🏗️ Structure du projet

```
pharma-delivery/
├── app/                      # Code source principal
│   ├── __init__.py           # Initialisation de l'application
│   ├── models/               # Modèles de données
│   ├── routes/               # Routes de l'API
│   ├── services/             # Logique métier
│   ├── static/               # Fichiers statiques
│   └── templates/            # Templates Jinja2
├── migrations/               # Migrations de base de données
├── tests/                    # Tests unitaires et d'intégration
├── .env.example              # Exemple de configuration
├── .gitignore               
├── config.py                # Configuration de l'application
├── requirements.txt          # Dépendances de production
├── requirements-dev.txt      # Dépendances de développement
└── README.md
```

## 📝 Bonnes pratiques de codage

### Style de code

- Suivez le [PEP 8](https://www.python.org/dev/peps/pep-0008/) pour le code Python
- Utilisez [Black](https://github.com/psf/black) pour le formatage automatique
- Vérifiez votre code avec [Flake8](https://flake8.pycqa.org/)
- Documentez votre code avec des docstrings suivant la [convention Google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

### Structure des commits

- Utilisez des messages de commit clairs et descriptifs
- Suivez la convention [Conventional Commits](https://www.conventionalcommits.org/)
- Exemple : `feat(auth): ajouter la connexion avec Google`

### Branches

- `main` - Branche principale, code stable et testé
- `develop` - Branche d'intégration pour les fonctionnalités en cours
- `feature/*` - Nouvelles fonctionnalités
- `bugfix/*` - Corrections de bogues
- `hotfix/*` - Corrections critiques pour la production

## 🧪 Tests

### Exécuter les tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=app tests/

# Un test spécifique
pytest tests/test_auth.py::test_login
```

### Écrire des tests

- Un test par fonctionnalité
- Utilisez des fixtures pour la configuration
- Testez les cas limites et les erreurs
- Visez une couverture de code élevée (au moins 80%)

## 🔄 Soumission de modifications

1. **Mettez à jour** votre branche principale :
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Créez une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

3. **Faites vos modifications** et committez :
   ```bash
   git add .
   git commit -m "feat(module): description des modifications"
   ```

4. **Poussez** vos modifications :
   ```bash
   git push -u origin feature/nom-de-la-fonctionnalite
   ```

5. **Ouvrez une Pull Request** vers la branche `main` du dépôt principal.

## 🐛 Signaler des bogues

Si vous trouvez un bogue, merci de créer une issue avec :

1. Un titre clair et descriptif
2. Les étapes pour reproduire le bogue
3. Le comportement attendu
4. Le comportement actuel
5. Captures d'écran si applicable
6. Version de l'application et de l'environnement

## 💡 Proposer des fonctionnalités

Nous apprécions les suggestions d'amélioration ! Pour proposer une nouvelle fonctionnalité :

1. Vérifiez qu'elle n'a pas déjà été proposée
2. Décrivez clairement la fonctionnalité
3. Expliquez pourquoi elle serait utile
4. Proposez une ébauche de solution si possible

## 👁️‍🗨️ Revue de code

Toutes les contributions passent par un processus de revue de code. Voici comment cela fonctionne :

1. Un mainteneur examinera votre PR
2. Des commentaires ou des demandes de modifications peuvent être faits
3. Une fois approuvé, votre PR sera fusionné

## ❓ Questions

Pour toute question, vous pouvez :

- Ouvrir une issue sur GitHub
- Nous contacter à [votre-email@exemple.com](mailto:votre-email@exemple.com)
- Rejoindre notre [espace de discussion](https://github.com/votre-utilisateur/pharmadelivery/discussions)

## 🙏 Remerciements

Merci à tous les [contributeurs](https://github.com/votre-utilisateur/pharmadelivery/graphs/contributors) qui ont aidé à faire de PharmaDelivery un meilleur outil !

---

Ce guide s'inspire du [Guide de contribution de l'Atom](https://github.com/atom/atom/blob/master/CONTRIBUTING.md).
