from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from dotenv import load_dotenv
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from pathlib import Path
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
csrf = CSRFProtect()
csrf.init_app(app)

# SQLite stores the local database in one file; no database server is required.
DATABASE_PATH = Path(os.getenv('DB_PATH', str(Path(app.root_path) / 'database' / 'yasmind.sqlite3')))
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect_database():
    """Create a SQLite connection for the current worker thread."""
    connection = sqlite3.connect(str(DATABASE_PATH), timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection

# Flask can serve requests on different threads. Keep a separate SQLite
# connection and cursor per thread instead of sharing one global connection.
import threading
_database_local = threading.local()

def get_thread_connection():
    connection = getattr(_database_local, 'connection', None)
    if connection is None:
        connection = connect_database()
        _database_local.connection = connection
        _database_local.cursor = connection.cursor()
    return connection

class DictionaryCursor:
    # Preserve the existing route code while providing a cursor per thread.
    def _cursor(self):
        get_thread_connection()
        return _database_local.cursor

    def execute(self, query, params=()):
        query = query.replace('%s', '?').replace('CURDATE()', "date('now', 'localtime')")
        return self._cursor().execute(query, params)

    def fetchone(self):
        row = self._cursor().fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(row) for row in self._cursor().fetchall()]

    @property
    def lastrowid(self):
        return self._cursor().lastrowid

    @property
    def rowcount(self):
        return self._cursor().rowcount

class DatabaseProxy:
    """Expose commit() on the current thread's SQLite connection."""
    def commit(self):
        get_thread_connection().commit()

def initialize_database():
    schema_path = Path(app.root_path) / 'schema.sql'
    connection = connect_database()
    try:
        connection.executescript(schema_path.read_text(encoding='utf-8'))
        connection.commit()
    finally:
        connection.close()

initialize_database()
db = DatabaseProxy()
cursor = DictionaryCursor()

@app.template_filter('format_date')
def format_date(value, output_format='%d/%m/%Y'):
    """Format SQLite date/timestamp strings and Python date objects safely."""
    if value is None or value == '':
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime(output_format)
    text_value = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text_value.replace('Z', '+00:00'))
        return parsed.strftime(output_format)
    except (ValueError, TypeError):
        # For a date-only string, datetime.fromisoformat normally handles it;
        # keep the original value visible if it has an unexpected format.
        return text_value

def password_matches(stored_password, supplied_password):
    """Verify a Werkzeug password hash, with legacy plaintext support for old local databases.

    Legacy plaintext passwords should be migrated to hashes before deployment.
    """
    if not stored_password:
        return False
    try:
        if stored_password.startswith(('scrypt:', 'pbkdf2:')):
            return check_password_hash(stored_password, supplied_password)
    except (ValueError, TypeError):
        return False
    return stored_password == supplied_password

# Login decorator
def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('home'))
            if session.get('role') != role:
                flash('Unauthorized access')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cursor.fetchone()
        
        if student and password_matches(student.get('password'), password):
            session.clear()
            session['user_id'] = student['id']
            session['name'] = student['name']
            session['role'] = 'student'
            return redirect(url_for('student_dashboard'))
            
        flash('Invalid credentials')
    return render_template('student/login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
        teacher = cursor.fetchone()
        
        if teacher and password_matches(teacher.get('password'), password):
            session.clear()
            session['user_id'] = teacher['id']
            session['name'] = teacher['name']
            session['role'] = 'teacher'
            return redirect(url_for('teacher_dashboard'))
            
        flash('Invalid credentials')
    return render_template('teacher/login.html')

class LoginForm(FlaskForm):
    pass

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        admin = cursor.fetchone()
        
        if admin and password_matches(admin.get('password'), password):
            session.clear()
            session['user_id'] = admin['id']
            session['name'] = admin['name']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
            
        flash('Invalid credentials')
    return render_template('admin/login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Teacher routes
# Add these new routes
@app.route('/teacher/courses')
@login_required('teacher')
def teacher_courses():
    cursor.execute("""
        SELECT c.*, m.name as module_name 
        FROM courses c
        JOIN modules m ON c.module_id = m.id
        WHERE m.teacher_id = %s
    """, (session['user_id'],))
    courses = cursor.fetchall()
    
    return render_template('teacher/courses.html', 
                         courses=courses,
                         teacher={'name': session['name']})  # Add this line

# Add these configurations
UPLOAD_FOLDER = str(Path(app.root_path) / 'static' / 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/teacher/add_course', methods=['GET', 'POST'])
@login_required('teacher')
def add_course():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        module_id = request.form.get('module_id', '').strip()
        content_type = request.form.get('content_type', '').lower().strip()
        description = request.form.get('description', '').strip()
        if not title or not module_id or content_type not in ALLOWED_EXTENSIONS:
            flash('Veuillez renseigner un titre, un module et un type de contenu valide')
            return redirect(request.url)
        cursor.execute("SELECT id FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
        if not cursor.fetchone():
            flash('Module non autorisé')
            return redirect(request.url)
        
        # Handle file upload
        if 'course_file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
            
        file = request.files['course_file']
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
            
        if file and allowed_file(file.filename) and file.filename.rsplit('.', 1)[1].lower() == content_type:
            filename = secure_filename(file.filename)
            if not filename:
                flash('Nom de fichier invalide')
                return redirect(request.url)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save course info to database
            cursor.execute("""
                INSERT INTO courses (module_id, title, content_type, description, file_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (module_id, title, content_type, description, filename))
            db.commit()
            
            flash('Cours ajouté avec succès')
            return redirect(url_for('teacher_courses'))
        flash('Le fichier doit être au format choisi : PDF, MP4 ou TXT')
        return redirect(request.url)
    
    # Get modules for the form
    cursor.execute("SELECT * FROM modules WHERE teacher_id = %s", (session['user_id'],))
    modules = cursor.fetchall()
    return render_template('teacher/add_course.html', modules=modules)

@app.route('/teacher/classes')
@login_required('teacher')
def teacher_classes():
    cursor.execute("""
        SELECT DISTINCT c.* 
        FROM classes c
        JOIN modules m ON c.id = m.class_id
        WHERE m.teacher_id = %s
    """, (session['user_id'],))
    classes = cursor.fetchall()
    return render_template('teacher/classes.html', classes=classes)

@app.route('/teacher/reports')
@login_required('teacher')
def teacher_reports():
    cursor.execute("""
        SELECT m.name as module_name, 
               COUNT(DISTINCT s.id) as student_count,
               AVG(g.grade) as average_grade
        FROM modules m
        LEFT JOIN grades g ON m.id = g.module_id
        LEFT JOIN students s ON g.student_id = s.id
        WHERE m.teacher_id = %s
        GROUP BY m.id
    """, (session['user_id'],))
    reports = cursor.fetchall()
    return render_template('teacher/reports.html', reports=reports)

# Update the teacher_dashboard route
@app.route('/teacher/dashboard')
@login_required('teacher')
def teacher_dashboard():
    # Get teacher's modules
    cursor.execute("""
        SELECT m.*, COUNT(DISTINCT s.id) as total_students, 
               AVG(g.grade) as average_grade
        FROM modules m 
        LEFT JOIN grades g ON m.id = g.module_id
        LEFT JOIN students s ON g.student_id = s.id
        WHERE m.teacher_id = %s
        GROUP BY m.id
    """, (session['user_id'],))
    modules = cursor.fetchall()
    
    # Get recent activities
    cursor.execute("""
        SELECT activity AS description, created_at
        FROM activity_logs
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (session['user_id'],))
    activities = cursor.fetchall()

    return render_template('teacher/dashboard.html', 
                         teacher={'name': session['name']},
                         modules=modules,
                         activities=activities)

@app.route('/teacher/grades/<int:module_id>')
@login_required('teacher')
def manage_grades(module_id):
    cursor.execute("""
        SELECT s.*, g.grade 
        FROM students s
        LEFT JOIN grades g ON s.id = g.student_id AND g.module_id = %s
    """, (module_id,))
    students = cursor.fetchall()
    
    cursor.execute("SELECT * FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
    module = cursor.fetchone()
    if not module:
        flash('Module introuvable ou accès non autorisé')
        return redirect(url_for('teacher_grades'))
    
    return render_template('teacher/grades.html', 
                         students=students, 
                         module=module)

@app.route('/teacher/attendance/<int:module_id>')
@login_required('teacher')
def take_attendance(module_id):
    cursor.execute("SELECT id FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
    if not cursor.fetchone():
        flash('Module introuvable ou accès non autorisé')
        return redirect(url_for('teacher_attendance'))
    cursor.execute("""
        SELECT s.*, a.status, a.date
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id 
        AND a.module_id = %s AND a.date = CURDATE()
    """, (module_id,))
    students = cursor.fetchall()
    
    return render_template('teacher/attendance.html', 
                         students=students, 
                         module_id=module_id)

# Add this new route for student dashboard
@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    # Get student's grades - removed the date field since it doesn't exist
    cursor.execute("""
        SELECT m.name as module_name, g.grade
        FROM grades g
        JOIN modules m ON g.module_id = m.id
        WHERE g.student_id = %s
        ORDER BY g.module_id
    """, (session['user_id'],))
    grades = cursor.fetchall()
    
    # Get attendance records
    cursor.execute("""
        SELECT m.name as module_name, a.date, a.status
        FROM attendance a
        JOIN modules m ON a.module_id = m.id
        WHERE a.student_id = %s
        ORDER BY a.date DESC
    """, (session['user_id'],))
    attendance = cursor.fetchall()
    
    return render_template('student/dashboard.html',
                         student={'name': session['name']},
                         grades=grades,
                         attendance=attendance)

@app.route('/student/courses')
@login_required('student')
def student_courses():
    cursor.execute("""
        SELECT m.name as module_name, c.title, c.description, c.content_type
        FROM modules m
        JOIN courses c ON m.id = c.module_id
    """)
    courses = cursor.fetchall()
    return render_template('student/courses.html', 
                         courses=courses,
                         student={'name': session['name']})  # Add this line

@app.route('/student/grades')
@login_required('student')
def student_grades():
    cursor.execute("""
        SELECT m.name as module_name, g.grade
        FROM grades g
        JOIN modules m ON g.module_id = m.id
        WHERE g.student_id = %s
        ORDER BY m.name
    """, (session['user_id'],))
    grades = cursor.fetchall()
    return render_template('student/grades.html', 
                         grades=grades,
                         student={'name': session['name']})

@app.route('/student/attendance')
@login_required('student')
def student_attendance():
    # Get modules summary
    cursor.execute("""
        SELECT DISTINCT
            m.name as module_name,
            COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absences,
            ROUND(
                COALESCE(
                    COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / NULLIF(COUNT(a.status), 0),
                    0
                ), 1
            ) as presence_rate
        FROM modules m
        JOIN grades g ON m.id = g.module_id
        LEFT JOIN attendance a ON m.id = a.module_id AND a.student_id = %s
        WHERE g.student_id = %s
        GROUP BY m.id, m.name
    """, (session['user_id'], session['user_id']))
    modules_summary = cursor.fetchall()

    # Get attendance records for specific dates
    cursor.execute("""
        SELECT m.name as module_name, a.date, a.status
        FROM modules m
        JOIN grades g ON m.id = g.module_id
        LEFT JOIN attendance a ON m.id = a.module_id AND a.student_id = %s
        WHERE g.student_id = %s AND a.date IS NOT NULL
        ORDER BY a.date DESC
    """, (session['user_id'], session['user_id']))
    attendance = cursor.fetchall()
    
    return render_template('student/attendance.html', 
                         attendance=attendance,
                         modules_summary=modules_summary,
                         student={'name': session['name']})

@app.route('/student/profile')
@login_required('student')
def student_profile():
    cursor.execute("""
        SELECT id, name, email FROM students 
        WHERE id = %s
    """, (session['user_id'],))
    student = cursor.fetchone()
    
    return render_template('student/profile.html', 
                         student=student)

@app.route('/teacher/profile')
@login_required('teacher')
def teacher_profile():
    cursor.execute("""
        SELECT id, name, email FROM teachers 
        WHERE id = %s
    """, (session['user_id'],))
    teacher = cursor.fetchone()
    
    return render_template('teacher/profile.html', 
                         teacher=teacher)

@app.route('/teacher/grades')
@login_required('teacher')
def teacher_grades():
    # Get all modules for this teacher
    cursor.execute("""
        SELECT * FROM modules 
        WHERE teacher_id = %s
    """, (session['user_id'],))
    modules = cursor.fetchall()
    
    # If no module is selected, just show the module selection page
    if not modules:
        return render_template('teacher/grades.html', 
                             modules=[],
                             students=[],
                             current_module=None)
    
    # Get the selected module ID from query parameters
    current_module_id = request.args.get('module_id')
    if not current_module_id:
        current_module_id = modules[0]['id']  # Default to first module
    
    # Get the current module info
    cursor.execute("""
        SELECT * FROM modules 
        WHERE id = %s AND teacher_id = %s
    """, (current_module_id, session['user_id']))
    current_module = cursor.fetchone()
    
    # Get students and their grades for the selected module
    cursor.execute("""
        SELECT s.*, g.grade 
        FROM students s
        LEFT JOIN grades g ON s.id = g.student_id AND g.module_id = %s
        WHERE EXISTS (
            SELECT 1 FROM modules m 
            WHERE m.id = %s AND m.teacher_id = %s
        )
    """, (current_module_id, current_module_id, session['user_id']))
    students = cursor.fetchall()
    
    # Calculate class average
    grades = [s['grade'] for s in students if s['grade'] is not None]
    class_average = sum(grades) / len(grades) if grades else 0
    
    return render_template('teacher/grades.html',
                         modules=modules,
                         current_module=current_module,
                         students=students,
                         class_average=class_average)

@app.route('/teacher/attendance', methods=['GET', 'POST'])
@login_required('teacher')
def teacher_attendance():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        action = data.get('action')
        
        if action == 'mark':
            student_id = data.get('student_id')
            module_id = data.get('module_id')
            status = data.get('status')
            date = data.get('date') or datetime.now().date().isoformat()
            if not student_id or not module_id or status not in ('present', 'absent'):
                return jsonify({'success': False, 'message': 'Données invalides'}), 400
            cursor.execute("SELECT id FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Module non autorisé'}), 403
            cursor.execute("SELECT id FROM grades WHERE student_id = %s AND module_id = %s", (student_id, module_id))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Étudiant non inscrit à ce module'}), 400
            try:
                cursor.execute("""
                    INSERT INTO attendance (student_id, module_id, date, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(student_id, module_id, date) DO UPDATE SET status = excluded.status
                """, (student_id, module_id, date, status))
                db.commit()
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
                
        elif action == 'save':
            # Simply return success as the attendance records are already saved
            return jsonify({'success': True, 'message': 'Attendance saved successfully'})
    
    # Get all modules for this teacher
    cursor.execute("SELECT * FROM modules WHERE teacher_id = %s", (session['user_id'],))
    modules = cursor.fetchall()
    
    if not modules:
        return render_template('teacher/attendance.html', 
                             modules=[],
                             students=[],
                             attendance_rate=0,
                             absence_rate=0)

    # Get the selected module ID from query parameters or default to first module
    current_module_id = request.args.get('module_id')
    if not current_module_id and modules:
        current_module_id = modules[0]['id']
    allowed_module_ids = {str(item['id']) for item in modules}
    if str(current_module_id) not in allowed_module_ids:
        current_module_id = modules[0]['id']

    # Get students and their attendance status for the selected module
    cursor.execute("""
        SELECT DISTINCT s.id, s.name, s.email, a.status 
        FROM students s
        JOIN grades g ON s.id = g.student_id
        LEFT JOIN attendance a ON s.id = a.student_id 
            AND a.module_id = %s 
            AND a.date = %s
        WHERE g.module_id = %s
        ORDER BY s.name
    """, (current_module_id, datetime.now().date(), current_module_id))
    students = cursor.fetchall()

    # Calculate attendance rates
    total_students = len(students)
    present_count = sum(1 for s in students if s['status'] == 'present')
    absent_count = sum(1 for s in students if s['status'] == 'absent')
    
    attendance_rate = (present_count / total_students * 100) if total_students > 0 else 0
    absence_rate = (absent_count / total_students * 100) if total_students > 0 else 0

    return render_template('teacher/attendance.html',
                         modules=modules,
                         students=students,
                         current_module_id=current_module_id,
                         attendance_rate=round(attendance_rate, 1),
                         absence_rate=round(absence_rate, 1))

@app.route('/teacher/update_attendance', methods=['POST'])
@login_required('teacher')
def update_attendance():
    data = request.get_json(silent=True) or {}
    student_id = data.get('student_id')
    module_id = data.get('module_id')
    status = data.get('status')
    attendance_date = data.get('date') or datetime.now().date().isoformat()
    if not student_id or not module_id or status not in ('present', 'absent'):
        return jsonify({'success': False, 'error': 'Données de présence invalides'}), 400

    # A teacher can only update attendance for their own modules and enrolled students.
    cursor.execute("SELECT id FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
    if not cursor.fetchone():
        return jsonify({'success': False, 'error': 'Module non autorisé'}), 403
    cursor.execute("SELECT id FROM grades WHERE student_id = %s AND module_id = %s", (student_id, module_id))
    if not cursor.fetchone():
        return jsonify({'success': False, 'error': 'Étudiant non inscrit à ce module'}), 400

    try:
        cursor.execute("""
            INSERT INTO attendance (student_id, module_id, date, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT(student_id, module_id, date) DO UPDATE SET status = excluded.status
        """, (student_id, module_id, attendance_date, status))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/teacher/attendance_history', methods=['GET'])
@login_required('teacher')
def attendance_history():
    module_id = request.args.get('module_id')
    
    cursor.execute("""
        SELECT DISTINCT a.date, 
            COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
            COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_count
        FROM attendance a
        WHERE a.module_id = %s
        GROUP BY a.date
        ORDER BY a.date DESC
    """, (module_id,))
    history = cursor.fetchall()
    
    # Get module name
    cursor.execute("SELECT name FROM modules WHERE id = %s AND teacher_id = %s", (module_id, session['user_id']))
    module = cursor.fetchone()
    
    return jsonify({
        'success': True,
        'history': history,
        'module_name': module['name'] if module else ''
    })

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    # Get basic statistics
    cursor.execute("SELECT COUNT(*) as count FROM students")
    students_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM teachers")
    teachers_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM modules")
    modules_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM classes")
    classes_count = cursor.fetchone()['count']
    
    stats = {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'modules_count': modules_count,
        'classes_count': classes_count
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@login_required('admin')
def admin_users():
    # Get all users (students and teachers)
    cursor.execute("SELECT id, name, email, 'student' as role FROM students")
    students = cursor.fetchall()
    
    cursor.execute("SELECT id, name, email, 'teacher' as role FROM teachers")
    teachers = cursor.fetchall()
    
    # Combine all users
    users = students + teachers
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/courses')
@login_required('admin')
def admin_courses():
    # Get all courses with their module and teacher information
    cursor.execute("""
        SELECT m.name as module_name, 
               t.name as teacher_name,
               m.id as module_id,
               t.id as teacher_id
        FROM modules m
        JOIN teachers t ON m.teacher_id = t.id
    """)
    courses = cursor.fetchall()
    
    # Get all teachers for the add course form
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    
    return render_template('admin/courses.html', courses=courses, teachers=teachers)

@app.route('/admin/departments')
@login_required('admin')
def admin_departments():
    # Get all departments with basic info first
    cursor.execute("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM modules WHERE class_id = c.id) as modules_count,
               (SELECT COUNT(DISTINCT teacher_id) FROM modules WHERE class_id = c.id) as teachers_count,
               (SELECT COUNT(DISTINCT s.id) 
                FROM students s 
                JOIN grades g ON s.id = g.student_id 
                JOIN modules m ON g.module_id = m.id 
                WHERE m.class_id = c.id) as students_count
        FROM classes c
    """)
    departments = cursor.fetchall()
    
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/settings')
@login_required('admin')
def admin_settings():
    # Get current admin info
    cursor.execute("SELECT id, name, email FROM admin WHERE id = %s", (session['user_id'],))
    admin = cursor.fetchone()
    
    return render_template('admin/settings.html', admin=admin)

@app.route('/admin/update_settings', methods=['POST'])
@login_required('admin')
def admin_update_settings():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    if not name or not email:
        flash('Le nom et l’email sont obligatoires')
        return redirect(url_for('admin_settings'))
    
    if password:
        # Update with new password
        cursor.execute("""
            UPDATE admin 
            SET name = %s, email = %s, password = %s 
            WHERE id = %s
        """, (name, email, generate_password_hash(password), session['user_id']))
    else:
        # Update without changing password
        cursor.execute("""
            UPDATE admin 
            SET name = %s, email = %s 
            WHERE id = %s
        """, (name, email, session['user_id']))
    
    db.commit()
    flash('Settings updated successfully')
    return redirect(url_for('admin_settings'))

# Remove the duplicate logout route here

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1')