# Historique des modifications

Ce document répertorie toutes les modifications notables apportées au projet PharmaDelivery, en suivant les principes de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [Non publié]
### Ajouté
- Structure de base du projet avec Flask et SQLAlchemy
- Configuration de déploiement Vercel
- Documentation complète (README, CONTRIBUTING, CODE_OF_CONDUCT, etc.)
- Gestion des dépendances avec requirements.txt
- Configuration pour le développement local

### Modifié
- Organisation des fichiers de configuration
- Documentation des variables d'environnement
- Structure des dossiers pour une meilleure maintenabilité

### Supprimé
- Fichiers inutiles et configurations obsolètes

## [0.1.0] - 2025-06-27
### Ajouté
- Version initiale du projet
- Configuration de base pour le déploiement Vercel
- Documentation de base

---

## À propos de ce format de CHANGELOG

### Format des versions

Chaque version suit le format [SemVer](https://semver.org/):
- **MAJOR** : Changements incompatibles avec les versions antérieures
- **MINOR** : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

### Types de modifications

- **Ajouté** pour les nouvelles fonctionnalités.
- **Modifié** pour les changements dans les fonctionnalités existantes.
- **Déprécié** pour les fonctionnalités qui seront bientôt supprimées.
- **Supprimé** pour les fonctionnalités supprimées.
- **Corrigé** pour toute correction de bug.
- **Sécurité** en cas de vulnérabilités corrigées.

## Comment mettre à jour ce fichier

1. Créez une nouvelle section `## [x.y.z] - YYYY-MM-DD` en haut du fichier.
2. Ajoutez les modifications sous les catégories appropriées.
3. Mettez à jour la version non publiée avec les modifications futures.
4. Conservez ce guide à la fin du fichier.
