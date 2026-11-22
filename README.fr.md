# YasMind — Plateforme de gestion des étudiants

<p align="center">
  <strong>Une plateforme web pour centraliser la gestion des activités académiques.</strong>
  <br />
  Développée avec Python, Flask et SQLite.
</p>

<p align="center">
  <a href="README.md">Read in English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</p>

---

## Présentation

**YasMind** est une plateforme web de gestion des étudiants qui regroupe les principales activités académiques au sein d'une seule application.

Elle propose des espaces adaptés aux étudiants, aux enseignants et aux administrateurs afin de faciliter l'organisation des informations académiques et les tâches de gestion quotidiennes.

## Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| Espace étudiant | Consulter les informations de l'étudiant, les cours, les notes et les présences. |
| Espace enseignant | Accéder aux pages et aux fonctionnalités destinées aux enseignants. |
| Administration | Disposer d'une interface administrative pour gérer les informations de la plateforme. |
| Gestion des cours | Organiser les informations relatives aux cours et aux modules. |
| Suivi des notes | Consulter et gérer les résultats académiques. |
| Suivi des présences | Consulter les enregistrements et les récapitulatifs des présences. |
| Base de données | Stocker les données de l'application avec SQLite. |
| Sécurité | Gestion des mots de passe, contrôle d'accès par session et protection CSRF. |

*Les actions disponibles dépendent du rôle de l'utilisateur et des fonctionnalités implémentées.*

## Technologies utilisées

- **Backend :** Python, Flask
- **Base de données :** SQLite
- **Frontend :** HTML5, CSS3, JavaScript, Jinja2
- **Accès aux données :** module Python `sqlite3`
- **Sécurité :** outils de hachage des mots de passe de Werkzeug et protection CSRF avec Flask-WTF

## Structure du projet

```text
YasMind/
├── app.py
├── schema.sql
├── seed_demo.py
├── requirements.txt
├── .env.example
├── .gitignore
├── database/
├── templates/
│   ├── student/
│   ├── teacher/
│   └── admin/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── uploads/
```

*Cette structure présente les principaux composants de l'application. Certains dossiers peuvent varier selon la version du dépôt.*

## Installation et démarrage

### Prérequis

- Python 3.10 ou version ultérieure recommandée
- Git (facultatif, pour cloner le dépôt)

### 1. Cloner le dépôt

```bash
git clone https://github.com/yasmine-salama/YasMind.git
cd YasMind
```

Accédez au dossier contenant `app.py` si celui-ci se trouve dans un sous-dossier.

### 2. Créer un environnement virtuel

**Windows — PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Si le projet contient un fichier `.env.example`, copiez-le vers `.env` et configurez les valeurs nécessaires.

Ne publiez jamais de mots de passe réels, de clés secrètes ou de paramètres privés.

### 5. Initialiser la base de données de démonstration

```bash
python seed_demo.py
```

Exécutez cette commande depuis le dossier contenant `seed_demo.py`.

### 6. Lancer l'application

```bash
python app.py
```

Ouvrez ensuite l'adresse suivante dans votre navigateur :

```text
http://127.0.0.1:5000
```

## Comptes de démonstration

Le script d'initialisation fournit des comptes de démonstration destinés aux tests locaux.

| Rôle | Adresse e-mail | Mot de passe |
|---|---|---|
| Étudiant | `student@example.test` | `Demo123!` |
| Enseignant | `teacher@example.test` | `Demo123!` |
| Administrateur | `admin@example.test` | `Demo123!` |

**Important :** ces identifiants sont réservés au développement. Ne les utilisez pas en production ni avec des données réelles d'étudiants.

## Sécurité

- Ne versionnez pas les clés secrètes ni les paramètres propres à votre environnement.
- Ne publiez pas de bases de données privées, de données réelles d'étudiants ou de fichiers sensibles.
- Utilisez des identifiants forts et uniques en dehors de l'environnement de démonstration.
- Vérifiez les autorisations avant tout déploiement public.

## État du projet

YasMind est un projet en cours de développement. Les fonctionnalités et les interfaces peuvent évoluer au fil des améliorations et des tests.

## Langues

- **English:** [Read the English documentation](README.md)
- **Français :** `README.fr.md`

## Licence

Aucune licence n'a encore été spécifiée. Sans licence ajoutée au dépôt, la réutilisation et la redistribution ne sont pas automatiquement autorisées.
