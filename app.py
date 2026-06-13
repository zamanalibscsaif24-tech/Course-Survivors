from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import webbrowser
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'course_survivors_iba_2024'
DB_PATH = '/var/data/course_survivors.db'

# ─── All courses from the BS AI curriculum PDF ───────────────────────────────
COURSES = [
    # Semester 1
    {"code": "CS102", "name": "Programming Fundamentals",                    "dept": "Computing Core",        "semester": 1, "credits": 4},
    {"code": "GE101", "name": "Application of ICT",                          "dept": "General Education",     "semester": 1, "credits": 3},
    {"code": "GE102", "name": "Islamic Studies / Ethics",                    "dept": "General Education",     "semester": 1, "credits": 2},
    {"code": "GE104", "name": "Discrete Structures",                         "dept": "General Education",     "semester": 1, "credits": 3},
    {"code": "GE105", "name": "Functional English",                          "dept": "General Education",     "semester": 1, "credits": 3},
    # Semester 2
    {"code": "CS150", "name": "Object Oriented Programming",                 "dept": "Computing Core",        "semester": 2, "credits": 4},
    {"code": "CS151", "name": "Database Systems",                            "dept": "Computing Core",        "semester": 2, "credits": 4},
    {"code": "GE150", "name": "Applied Physics",                             "dept": "General Education",     "semester": 2, "credits": 3},
    {"code": "GE151", "name": "Calculus and Analytic Geometry",              "dept": "Mathematics",           "semester": 2, "credits": 3},
    {"code": "GE152", "name": "Expository Writing",                          "dept": "General Education",     "semester": 2, "credits": 3},
    # Semester 3
    {"code": "CS201", "name": "Data Structures",                             "dept": "Computing Core",        "semester": 3, "credits": 4},
    {"code": "CS202", "name": "Digital Logic Design",                        "dept": "Computing Core",        "semester": 3, "credits": 3},
    {"code": "CS203", "name": "Computer Networks",                           "dept": "Computing Core",        "semester": 3, "credits": 3},
    {"code": "CS204", "name": "Software Engineering",                        "dept": "Computing Core",        "semester": 3, "credits": 3},
    {"code": "GE201", "name": "Ideology and Constitution of Pakistan",        "dept": "General Education",     "semester": 3, "credits": 2},
    {"code": "MT201", "name": "Multivariate Calculus",                       "dept": "Mathematics",           "semester": 3, "credits": 3},
    # Semester 4
    {"code": "CS250", "name": "Computer Organization & Assembly Language",   "dept": "Computing Core",        "semester": 4, "credits": 3},
    {"code": "CS251", "name": "Theory of Automata",                          "dept": "Domain Core",           "semester": 4, "credits": 3},
    {"code": "CS252", "name": "Advanced Database Management Systems",        "dept": "Domain Core",           "semester": 4, "credits": 3},
    {"code": "CS253", "name": "Artificial Intelligence",                     "dept": "Computing Core",        "semester": 4, "credits": 3},
    {"code": "CS254", "name": "Information Security",                        "dept": "Computing Core",        "semester": 4, "credits": 3},
    {"code": "MT250", "name": "Probability & Statistics",                    "dept": "Mathematics",           "semester": 4, "credits": 3},
    # Semester 5
    {"code": "CS301", "name": "Operating Systems",                           "dept": "Computing Core",        "semester": 5, "credits": 3},
    {"code": "CS302", "name": "Compiler Construction",                       "dept": "Domain Core",           "semester": 5, "credits": 3},
    {"code": "CS303", "name": "Computer Architecture",                       "dept": "Domain Core",           "semester": 5, "credits": 3},
    {"code": "MT301", "name": "Linear Algebra",                              "dept": "Mathematics",           "semester": 5, "credits": 3},
    # Semester 6
    {"code": "CS350", "name": "HCI and Computer Graphics",                   "dept": "Domain Core",           "semester": 6, "credits": 3},
    {"code": "CS351", "name": "Parallel & Distributed Computing",            "dept": "Domain Core",           "semester": 6, "credits": 3},
    {"code": "CS352", "name": "Analysis of Algorithms",                      "dept": "Computing Core",        "semester": 6, "credits": 3},
    {"code": "EN350", "name": "Technical & Business Writing",                "dept": "Supporting",            "semester": 6, "credits": 3},
    # Semester 7
    {"code": "CS401", "name": "Final Year Project - I",                      "dept": "Computing Core",        "semester": 7, "credits": 2},
    {"code": "GE401", "name": "Entrepreneurship",                            "dept": "General Education",     "semester": 7, "credits": 2},
    {"code": "SS401", "name": "Introduction to Marketing",                   "dept": "Supporting",            "semester": 7, "credits": 3},
    # Semester 8
    {"code": "CS450", "name": "Final Year Project - II",                     "dept": "Computing Core",        "semester": 8, "credits": 4},
    {"code": "GE450", "name": "Introduction to Management",                  "dept": "General Education",     "semester": 8, "credits": 2},
    {"code": "GE451", "name": "Arts & Humanities (Professional Practices)",  "dept": "General Education",     "semester": 8, "credits": 2},
    {"code": "GE452", "name": "Civics and Community Engagement",             "dept": "General Education",     "semester": 8, "credits": 2},
    # Domain Electives (AI Specialization)
    {"code": "CS-AI1", "name": "Machine Learning",                           "dept": "AI Elective",           "semester": 5, "credits": 3},
    {"code": "CS-AI2", "name": "Deep Learning",                              "dept": "AI Elective",           "semester": 6, "credits": 3},
    {"code": "CS-AI3", "name": "Computer Vision",                            "dept": "AI Elective",           "semester": 7, "credits": 3},
    {"code": "CS-AI4", "name": "Natural Language Processing",                "dept": "AI Elective",           "semester": 7, "credits": 3},
    {"code": "CS-AI5", "name": "Data Science",                               "dept": "AI Elective",           "semester": 6, "credits": 3},
    {"code": "CS-AI6", "name": "Reinforcement Learning",                     "dept": "AI Elective",           "semester": 7, "credits": 3},
    {"code": "CS-AI7", "name": "Generative AI",                              "dept": "AI Elective",           "semester": 7, "credits": 3},
    {"code": "CS-AI8", "name": "MLOps",                                      "dept": "AI Elective",           "semester": 7, "credits": 3},
    {"code": "CS-E1",  "name": "Web Technologies",                           "dept": "Domain Elective",       "semester": 5, "credits": 3},
    {"code": "CS-E2",  "name": "Mobile Application Development",             "dept": "Domain Elective",       "semester": 5, "credits": 3},
    {"code": "CS-E3",  "name": "Cyber Security",                             "dept": "Domain Elective",       "semester": 6, "credits": 3},
    {"code": "CS-E4",  "name": "Cloud Computing",                            "dept": "Domain Elective",       "semester": 6, "credits": 3},
    {"code": "CS-E5",  "name": "Data Mining",                                "dept": "Domain Elective",       "semester": 6, "credits": 3},
    {"code": "CS-E6",  "name": "Blockchain Technologies",                    "dept": "Domain Elective",       "semester": 7, "credits": 3},
    {"code": "CS-E7",  "name": "Digital Image Processing",                   "dept": "Domain Elective",       "semester": 7, "credits": 3},
]

DEPT_COLORS = {
    "Computing Core":    ("primary",   "💻"),
    "Domain Core":       ("success",   "🔬"),
    "Mathematics":       ("warning",   "📐"),
    "General Education": ("secondary", "📚"),
    "AI Elective":       ("danger",    "🤖"),
    "Domain Elective":   ("info",      "⚡"),
    "Supporting":        ("dark",      "📝"),
}

# ─── Database ────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        points INTEGER DEFAULT 100,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        dept TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_code TEXT NOT NULL,
        difficulty INTEGER NOT NULL,
        workload INTEGER NOT NULL,
        professor_rating INTEGER NOT NULL,
        overall INTEGER NOT NULL,
        comment TEXT,
        tips TEXT,
        grade_received TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    # Seed courses
    for course in COURSES:
        c.execute('''INSERT OR IGNORE INTO courses (code, name, dept, semester, credits)
                     VALUES (?, ?, ?, ?, ?)''',
                  (course['code'], course['name'], course['dept'], course['semester'], course['credits']))
    conn.commit()
    conn.close()

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        if not name:
            flash('Please enter your full name.', 'danger')
        elif not email.endswith('@iba-suk.edu.pk'):
            flash('Only IBA Sukkur emails (@iba-suk.edu.pk) are allowed.', 'danger')
        else:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if not user:
                conn.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
                conn.commit()
                user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            conn.close()
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn    = get_db()
    user    = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user:
        conn.close()
        session.clear()
        flash('Session expired. Please sign in again.', 'warning')
        return redirect(url_for('index'))
    courses = conn.execute('SELECT * FROM courses ORDER BY semester, code').fetchall()

    # Aggregate stats per course
    stats = {}
    for row in conn.execute('''
        SELECT course_code,
               COUNT(*) as review_count,
               ROUND(AVG(overall), 1) as avg_overall,
               ROUND(AVG(difficulty), 1) as avg_difficulty
        FROM reviews GROUP BY course_code
    ''').fetchall():
        stats[row['course_code']] = dict(row)
    conn.close()

    search   = request.args.get('q', '').lower()
    dept_f   = request.args.get('dept', 'All')
    sem_f    = request.args.get('sem', 'All')

    filtered = []
    for c in courses:
        if search and search not in c['name'].lower() and search not in c['code'].lower():
            continue
        if dept_f != 'All' and c['dept'] != dept_f:
            continue
        if sem_f != 'All' and str(c['semester']) != sem_f:
            continue
        filtered.append(c)

    depts = sorted(set(c['dept'] for c in courses))
    return render_template('dashboard.html',
        user=user, courses=filtered, stats=stats,
        dept_colors=DEPT_COLORS, depts=depts,
        search=search, dept_f=dept_f, sem_f=sem_f,
        semesters=range(1, 9))

@app.route('/review/<course_code>', methods=['GET', 'POST'])
def review(course_code):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn   = get_db()
    course = conn.execute('SELECT * FROM courses WHERE code = ?', (course_code,)).fetchone()
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('dashboard'))

    reviews = conn.execute('''
        SELECT r.*, u.name as reviewer_name
        FROM reviews r JOIN users u ON r.user_id = u.id
        WHERE r.course_code = ?
        ORDER BY r.created_at DESC
    ''', (course_code,)).fetchall()

    existing = conn.execute('SELECT * FROM reviews WHERE user_id = ? AND course_code = ?',
                            (session['user_id'], course_code)).fetchone()

    if request.method == 'POST':
        if existing:
            flash('You have already reviewed this course.', 'warning')
        else:
            difficulty       = int(request.form['difficulty'])
            workload         = int(request.form['workload'])
            professor_rating = int(request.form['professor_rating'])
            overall          = int(request.form['overall'])
            comment          = request.form.get('comment', '').strip()
            tips             = request.form.get('tips', '').strip()
            grade_received   = request.form.get('grade_received', '')
            conn.execute('''INSERT INTO reviews
                (user_id, course_code, difficulty, workload, professor_rating, overall, comment, tips, grade_received)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session['user_id'], course_code, difficulty, workload,
                 professor_rating, overall, comment, tips, grade_received))
            conn.execute('UPDATE users SET points = points + 50 WHERE id = ?', (session['user_id'],))
            conn.commit()
            flash('Review submitted! You earned 50 points 🎉', 'success')
            conn.close()
            return redirect(url_for('review', course_code=course_code))

    conn.close()
    return render_template('review.html', course=course, reviews=reviews,
                           existing=existing, dept_colors=DEPT_COLORS)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn = get_db()
    users = conn.execute('''
        SELECT u.*, COUNT(r.id) as review_count
        FROM users u LEFT JOIN reviews r ON u.id = r.user_id
        GROUP BY u.id ORDER BY u.points DESC LIMIT 20
    ''').fetchall()
    me = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    if not me:
        session.clear()
        flash('Session expired. Please sign in again.', 'warning')
        return redirect(url_for('index'))
    return render_template('leaderboard.html', users=users, me=me)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = 5000
    url = f'http://127.0.0.1:{port}'
    # Open browser automatically after a short delay (so Flask starts first)
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    print(f"\n🎓 Course Survivors is running → {url}\n")
    app.run(debug=True, port=port, use_reloader=False)
