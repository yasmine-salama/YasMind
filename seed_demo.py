"""Create fictional demo accounts and sample data in the local SQLite database."""
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import DATABASE_PATH

conn = sqlite3.connect(str(DATABASE_PATH), timeout=15)
conn.row_factory = sqlite3.Row
conn.execute('PRAGMA foreign_keys = ON')
cur = conn.cursor()
demo_password = generate_password_hash('Demo123!')

try:
    cur.execute("INSERT OR IGNORE INTO classes (id, name, department, year) VALUES (1, 'Classe A', 'Informatique', 2)")
    cur.execute("INSERT OR IGNORE INTO classes (id, name, department, year) VALUES (2, 'Classe B', 'Informatique', 2)")
    for name, email in [('Alex Martin', 'teacher@example.test'), ('Sam Taylor', 'teacher2@example.test')]:
        cur.execute("INSERT OR IGNORE INTO teachers (name, email, password) VALUES (?, ?, ?)", (name, email, demo_password))
    cur.execute("INSERT OR IGNORE INTO students (name, email, password) VALUES (?, ?, ?)", ('Jordan Lee', 'student@example.test', demo_password))
    cur.execute("INSERT OR IGNORE INTO admin (name, email, password) VALUES (?, ?, ?)", ('Demo Admin', 'admin@example.test', demo_password))

    teacher_id = cur.execute("SELECT id FROM teachers WHERE email = 'teacher@example.test'").fetchone()['id']
    teacher2_id = cur.execute("SELECT id FROM teachers WHERE email = 'teacher2@example.test'").fetchone()['id']
    student_id = cur.execute("SELECT id FROM students WHERE email = 'student@example.test'").fetchone()['id']

    cur.execute("INSERT OR IGNORE INTO modules (name, teacher_id, class_id) SELECT 'Python', ?, 1 WHERE NOT EXISTS (SELECT 1 FROM modules WHERE name='Python' AND teacher_id=?)", (teacher_id, teacher_id))
    cur.execute("INSERT OR IGNORE INTO modules (name, teacher_id, class_id) SELECT 'Bases de données', ?, 2 WHERE NOT EXISTS (SELECT 1 FROM modules WHERE name='Bases de données' AND teacher_id=?)", (teacher2_id, teacher2_id))
    module_id = cur.execute("SELECT id FROM modules WHERE name='Python' AND teacher_id=? LIMIT 1", (teacher_id,)).fetchone()['id']
    cur.execute("INSERT OR IGNORE INTO grades (student_id, module_id, grade) VALUES (?, ?, 16.5)", (student_id, module_id))
    cur.execute("INSERT OR IGNORE INTO attendance (student_id, module_id, date, status) VALUES (?, ?, date('now', 'localtime'), 'present')", (student_id, module_id))
    conn.commit()
    print('Données de démonstration créées. Mot de passe commun : Demo123!')
    print('Étudiant : student@example.test | Enseignant : teacher@example.test | Admin : admin@example.test')
except Exception:
    conn.rollback()
    raise
finally:
    cur.close()
    conn.close()
