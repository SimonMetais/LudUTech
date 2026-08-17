# Contexte du Projet : JDSU (Jeux De Sociéte U)

Ce document sert de référence principale pour le développement du projet JDSU. Il doit être consulté et respecté lors de chaque modification du code.

## 1. Description du Projet
- **Objectif** : Application de gestion de ludothèque pour entreprise (jeux de société et jeux d'extérieur).
- **Public cible** : Employés d'une entreprise.
- **Accès** : Pas de système de connexion/authentification pour les utilisateurs standards. L'accès est libre pour la consultation et la réservation (selon les futures fonctionnalités).
- **Administration** : Seul l'administrateur dispose d'une interface protégée (Django Admin standard).

## 2. Conventions de Langue
- **Code (Variables, Classes, Fonctions, Fichiers)** : Strictement en **anglais**.
- **Interface Utilisateur (Labels, Textes, Messages)** : Strictement en **français**.
- **Documentation (Docstrings, Commentaires)** : Strictement en **français**.

## 3. Stack Technique
- **Framework** : Django.
- **Base de données** : SQLite (par défaut).
- **Gestionnaire de dépendances** : `uv`.
- **Exécution des commandes** : Toujours utiliser `uv run` pour exécuter les commandes (ex: `uv run manage.py ...`).

## 4. Structure du Code
- Le projet suit la structure standard Django.
- Les modèles liés aux jeux se trouvent dans `core/models/`.
- **Vues** : Il est recommandé de créer un fichier `.py` par vue dans le package `views/` (ex: `game_list.py`, `game_detail.py`).
- **Tests** : Les tests doivent être organisés dans des fichiers dédiés selon la convention Django (généralement dans un package `tests/` au sein de chaque application, avec des fichiers séparés par thématique : `test_models.py`, `test_views.py`, etc.).

## 5. Principes de Développement
- **Minimalisme JS** : Utiliser le moins de JavaScript possible.
- **Pythonique** : Le code doit être le plus "Pythonique" possible.
- **HTMX & Alpine.js** : En cas de besoin d'interactivité, passer prioritairement par HTMX et Alpine.js.
- **Modernité Web** : Profiter au maximum des dernières fonctionnalités de CSS et HTML avant de passer à d'autres solutions techniques.
- **Bonnes Pratiques Django** : 
    - Toujours implémenter `get_absolute_url()` sur les modèles ayant une vue de détail.
    - Utiliser `get_absolute_url()` dans les templates (`{{ obj.get_absolute_url }}`) et les vues (`redirect(obj)`) au lieu de `reverse()` ou du tag `{% url %}`.
    - Privilégier les slugs aux IDs dans les URLs pour un meilleur SEO et une meilleure lisibilité.
    - Utiliser `prepopulated_fields` dans l'administration pour les slugs.

## 6. Instructions pour l'IA
- Toujours vérifier ce fichier avant de proposer des changements.
- Respecter scrupuleusement le mélange Anglais (code) / Français (textes/doc).
- Privilégier la simplicité étant donné qu'il s'agit d'un "petit projet".
- Suivre les principes de développement (Minimalisme JS, HTMX, Alpine.js).
- **Processus de validation** : Les commandes `manage.py makemigrations` et `manage.py check` doivent toujours être effectuées en dernier lieu. L'IA doit systématiquement demander l'autorisation explicite à l'utilisateur avant d'exécuter ces commandes, afin de permettre à l'utilisateur de valider ou de compléter le travail sur les modèles.
