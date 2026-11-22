<div align="center">

# YasMind · EduSmart

**Application web de gestion pédagogique** — étudiants, enseignants, cours, notes et présences.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20app-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Projet%20acad%C3%A9mique-orange)

</div>

---

## Sommaire

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Organisation du projet](#-organisation-du-projet)
- [Prérequis](#-prérequis)
- [Installation et lancement](#-installation-et-lancement)
- [Comptes de démonstration](#-comptes-de-démonstration)
- [Base de données](#-base-de-données)
- [Sécurité et configuration](#-sécurité-et-configuration)
- [État actuel et pistes d'amélioration](#-état-actuel-et-pistes-damélioration)

## 🎓 Présentation

**YasMind / EduSmart** est un projet web académique conçu pour centraliser plusieurs opérations courantes d'un établissement d'enseignement. L'application propose des espaces distincts selon le rôle de l'utilisateur : **administrateur, enseignant ou étudiant**.

L'objectif est de fournir une interface unique pour consulter les informations pédagogiques, organiser les cours, suivre les notes et gérer les présences. Le serveur est développé en Python avec Flask, les pages sont rendues avec Jinja et les données sont stockées dans une base SQLite locale, conservée dans un seul fichier.

> **À savoir :** ce dépôt contient une base de projet à exécuter et à tester en local. Il ne s'agit pas d'une version certifiée pour une utilisation en production avec de vraies données d'étudiants.

## ✨ Fonctionnalités

### 👩‍🎓 Espace étudiant

- Tableau de bord avec un aperçu des notes et des présences.
- Consultation des cours disponibles.
- Consultation des notes par module.
- Historique et résumé des présences.
- Consultation du profil.

### 👨‍🏫 Espace enseignant

- Tableau de bord et liste des modules attribués.
- Consultation des cours et ajout de ressources pédagogiques aux formats PDF, MP4 et TXT.
- Consultation des notes et calcul de la moyenne d'un module.
- Enregistrement des présences pour les étudiants associés à un module.
- Consultation des classes et d'un récapitulatif des résultats par module.

### 🛠️ Espace administrateur

- Tableau de bord avec des statistiques de base.
- Consultation des comptes étudiants et enseignants.
- Consultation des modules.
- Consultation des classes et départements.
- Modification des paramètres du compte administrateur.

## 🧰 Technologies

| Technologie | Utilisation |
|---|---|
| Python | Logique de l'application et accès aux données |
| Flask | Routes HTTP et serveur web |
| Jinja2 | Rendu des pages HTML |
| HTML5 / CSS3 | Structure et mise en forme de l'interface |
| SQLite | Stockage relationnel dans un fichier local, sans serveur à installer |
| `sqlite3` | Module de connexion SQLite inclus dans Python |
| Flask-WTF / CSRFProtect | Protection CSRF des formulaires et requêtes concernées |
| Werkzeug | Gestion des mots de passe hachés et des noms de fichiers |

## 🗂️ Organisation du projet

```text
PROJET/
├── app.py                  # Routes Flask et logique principale
├── schema.sql              # Structure de la base SQLite
├── seed_demo.py            # Création de données fictives pour tester
├── requirements.txt        # Dépendances Python
├── .env.example            # Exemple de configuration locale
├── .gitignore              # Fichiers exclus de Git
├── README.md               # Documentation du projet
├── templates/
│   ├── index.html          # Page d'accueil
│   ├── student/            # Pages de l'espace étudiant
│   ├── teacher/            # Pages de l'espace enseignant
│   └── admin/               # Pages de l'espace administrateur
└── static/
    ├── css/                 # Feuilles de style
    ├── images/              # Images de l'interface
    └── uploads/             # Ressources téléversées (non versionnées)
```

## 💻 Prérequis

Installez les éléments suivants avant de commencer :

- Python **3.10 ou plus récent**.
- Aucun serveur de base de données requis : SQLite est inclus dans Python.
- Git, si vous clonez le dépôt.
- Un navigateur web récent.

## 🚀 Installation et lancement

Les commandes suivantes sont à exécuter depuis le dossier du projet, celui qui contient `app.py`.

### 1. Récupérer le projet

```bash
git clone <URL_DU_DEPOT>
cd PROJET
```

Remplacez `<URL_DU_DEPOT>` par l'URL du dépôt GitHub. Si vous avez déjà téléchargé le projet, ouvrez directement son dossier dans un terminal.

### 2. Créer un environnement virtuel

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Base de données SQLite

Aucune installation de SQLite, aucun serveur et aucun compte SQL ne sont nécessaires. Au premier lancement, l’application crée automatiquement `database/yasmind.sqlite3` à partir de `schema.sql`.

Le chemin peut être personnalisé dans un fichier `.env` :

```env
DB_PATH=database/yasmind.sqlite3
SECRET_KEY=remplacez-par-une-cle-aleatoire-longue
```

Le fichier `.sqlite3` contient les données locales et ne doit pas être publié sur GitHub. Le dossier `database/` est ignoré par Git, à l’exception d’un éventuel fichier `.gitkeep`.

### 5. Configuration facultative

Le projet fonctionne sans fichier `.env` : SQLite est créé automatiquement et une clé de session temporaire est générée pour le développement. Pour définir une clé stable en local, copiez `.env.example` vers `.env` et modifiez `SECRET_KEY`. Ne publiez jamais `.env`.

### 6. Ajouter des données fictives

Pour obtenir des comptes et quelques exemples de modules, exécutez :

```bash
python seed_demo.py
```

Cette étape est facultative si vous préférez créer vos propres données. Le script ajoute des données de démonstration sans écraser les comptes déjà présents.

### 7. Lancer le serveur

```bash
python app.py
```

Ouvrez ensuite l'adresse locale affichée par Flask, généralement : <http://127.0.0.1:5000>.

Arrêtez le serveur avec `Ctrl+C` dans le terminal.

## 🔐 Comptes de démonstration

Après l'exécution de `seed_demo.py`, les comptes fictifs suivants peuvent être utilisés :

| Rôle | Adresse e-mail | Mot de passe de démonstration |
|---|---|---|
| Administrateur | `admin@example.test` | `Demo123!` |
| Enseignant | `teacher@example.test` | `Demo123!` |
| Étudiant | `student@example.test` | `Demo123!` |

Ces identifiants sont **publics et réservés aux tests locaux**. Ne les utilisez jamais pour un compte réel ni sur un serveur accessible publiquement. Les mots de passe créés par le script sont hachés.

## 🗄️ Base de données

Le schéma comprend les tables principales suivantes :

- `students`, `teachers`, `admin` : comptes associés aux rôles.
- `classes` : classes et informations de département.
- `modules` : matières associées à un enseignant et, éventuellement, à une classe.
- `grades` : notes des étudiants par module.
- `attendance` : présence ou absence à une date donnée.
- `courses` : ressources pédagogiques liées aux modules.
- `activity_logs` : structure destinée aux activités affichées dans le tableau de bord.

`schema.sql` décrit la structure SQLite et est appliqué automatiquement au démarrage. `seed_demo.py` ajoute séparément des données fictives pour les tests.

## 🔒 Sécurité et configuration

Avant de publier ou de déployer ce projet :

- Gardez les secrets et les paramètres personnels dans `.env`, jamais dans le code source.
- Remplacez `SECRET_KEY` par une valeur aléatoire et privée.
- N'utilisez pas le mode debug sur un serveur public.
- Utilisez des mots de passe hachés et migrez les éventuels anciens mots de passe stockés en clair. Le code conserve une compatibilité avec les anciennes bases locales : cette compatibilité doit être retirée après migration.
- Ne publiez pas de fichiers téléversés, de données réelles d'étudiants, d'exports SQL ou de captures contenant des informations privées.
- Configurez un utilisateur SQLite dédié avec des droits limités plutôt que d'utiliser `root`.
- Contrôlez les règles d'accès, les validations de formulaire et les fichiers téléversés avant toute utilisation réelle.

## 🧭 État actuel et pistes d'amélioration

Le projet a été réorganisé pour faciliter son installation et sa publication : configuration par variables d'environnement, schéma de base de données séparé, données de démonstration distinctes, dépendances listées et fichiers locaux exclus de Git.

Les prochaines améliorations recommandées sont :

1. Ajouter des tests automatisés pour les routes, les rôles et les requêtes SQL.
2. Migrer tous les comptes existants vers le hachage des mots de passe et supprimer la compatibilité avec le texte clair.
3. Revoir les droits d'accès à toutes les routes et renforcer la validation des données.
4. Ajouter la pagination, la recherche et la gestion complète des utilisateurs, classes et modules.
5. Compléter la gestion des ressources : téléchargement contrôlé, suppression, validation du contenu et limites de taille.
6. Mettre en place une gestion d'erreurs de base de données plus robuste et une configuration de déploiement sécurisée.

---

<div align="center">

**YasMind / EduSmart** · Projet académique de gestion pédagogique

</div>
