# YasMind — Student Management Platform

<p align="center">
  <strong>A web-based platform for managing academic activities in one place.</strong>
  <br />
  Built with Python, Flask, and SQLite.
</p>

<p align="center">
  <a href="README.fr.md">Lire en français</a>
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

## Overview

**YasMind** is a web-based student management platform designed to bring essential academic activities together in a single application.

The platform provides role-based spaces for students, teachers, and administrators, helping organize academic information and simplify everyday management tasks.

## Features

| Feature | Description |
|---|---|
| Student Space | Access student information, courses, grades, and attendance records. |
| Teacher Space | Access teacher-related pages and academic management features. |
| Administration | Provide an administrative interface for managing platform information. |
| Course Management | Organize course and module information. |
| Grade Tracking | View and manage academic grade records. |
| Attendance Tracking | Consult attendance records and summaries. |
| Database Integration | Store application data using SQLite. |
| Security | Password handling, session-based access control, and CSRF protection. |

*Available actions depend on the user's role and the implemented functionality.*

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2
- **Database Access:** Python `sqlite3`
- **Security:** Werkzeug password utilities, Flask-WTF CSRF protection

## Project Structure

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

*The structure above illustrates the main application components; some folders may vary depending on the repository version.*

## Getting Started

### Prerequisites

- Python 3.10 or later recommended
- Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/yasmine-salama/YasMind.git
cd YasMind
```

Navigate to the directory containing `app.py` if it is inside a subfolder.

### 2. Create a virtual environment

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

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

If the project includes `.env.example`, copy it to `.env` and configure the required values.

Never publish real passwords, secret keys, or private configuration values.

### 5. Initialize the demo database

```bash
python seed_demo.py
```

Run the initialization command from the directory containing `seed_demo.py`.

### 6. Start the application

```bash
python app.py
```

Open the local application in your browser:

```text
http://127.0.0.1:5000
```

## Demo Accounts

The development seed script provides demo accounts for local testing.

| Role | Email | Password |
|---|---|---|
| Student | `student@example.test` | `Demo123!` |
| Teacher | `teacher@example.test` | `Demo123!` |
| Administrator | `admin@example.test` | `Demo123!` |

**Important:** These are development credentials only. Do not use them in production or with real student data.

## Security Notes

- Keep secret keys and environment-specific settings out of version control.
- Do not commit private databases, real student records, or sensitive uploaded files.
- Use strong, unique credentials outside the demo environment.
- Review access permissions before deploying the application publicly.

## Project Status

YasMind is a development project. Features and interfaces may evolve as the application is improved and tested.

## Language

- **English:** `README.md`
- **Français :** [Consulter la documentation française](README.fr.md)

## License

No license has been specified yet. Unless a license is added to the repository, reuse and redistribution are not automatically permitted.
