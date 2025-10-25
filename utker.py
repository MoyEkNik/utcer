from flask import Flask, render_template_string, request, jsonify, session, g
import hashlib
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = 'secret-key-12345'
DATABASE = 'quiz_database.db'

# --- Хеширование пароля (должно быть ДО init_db!) ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- SUBJECTS (остаются для демо, но не используются в логике) ---
SUBJECTS = {
    'school': {
        'name': '📚 Школьные предметы',
        'items': {
            'math': '📐 Математика',
            'russian': '📖 Русский язык',
            'literature': '📚 Литература',
            'english': '🔤 Английский язык',
            'history': '📜 История',
            'social_studies': '🏛️ Обществознание',
            'geography': '🌍 География',
            'biology': '🌿 Биология',
            'physics': '⚛️ Физика',
            'chemistry': '🧪 Химия',
            'informatics': '💻 Информатика',
            'python': '🐍 Программирование Python',
            'art': '🎨 ИЗО',
            'music': '🎵 Музыка',
            'pe': '⚽ Физкультура',
            'technology': '🔧 Технология',
            'obzh': '🚨 ОБЖ'
        }
    },
    'cdo': {
        'name': '🎨 Кружки ЦДО г. Мирный',
        'items': {
            'programming': '💻 Программирование',
            'robotics': '🤖 Робототехника',
            'design': '🎨 Графический дизайн',
            'dance': '💃 Танцы',
            'vocal': '🎤 Вокал',
            'theater': '🎭 Театральная студия',
            'art_studio': '🖼️ Художественная студия',
            'chess': '♟️ Шахматы',
            'foreign_languages': '🌍 Иностранные языки',
            'young_technician': '🔧 Юный техник',
            'ecology': '🌱 Экология',
            'local_history': '🏞️ Краеведение',
            'sports_sections': '🏃 Спортивные секции'
        }
    },
    'additional': {
        'name': '🎯 Дополнительные курсы',
        'items': {
            'web_design': '🌐 Веб-дизайн',
            'mobile_apps': '📱 Мобильные приложения',
            'data_science': '📊 Анализ данных',
            'cybersecurity': '🛡️ Кибербезопасность',
            'game_dev': '🎮 Разработка игр',
            'digital_art': '🖥️ Цифровое искусство',
            'video_editing': '🎬 Видеомонтаж',
            '3d_modeling': '🔄 3D-моделирование'
        }
    }
}

# --- DATABASE ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                subjects TEXT,
                class TEXT,
                school TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                difficulty TEXT NOT NULL,
                color TEXT NOT NULL,
                time TEXT,
                questions_count INTEGER DEFAULT 0,
                created_by TEXT NOT NULL,
                subject TEXT,
                is_custom BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                question_order INTEGER NOT NULL,
                FOREIGN KEY (test_id) REFERENCES tests (id) ON DELETE CASCADE
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                test_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES tests (id)
            )
        ''')
        db.commit()

        # Демо-пользователи
        db.execute(
            'INSERT OR IGNORE INTO users (username, password, role, name, subjects) VALUES (?, ?, ?, ?, ?)',
            ('teacher', hash_password('teacher123'), 'teacher', 'Учитель Python', '["python", "informatics"]')
        )
        db.execute(
            'INSERT OR IGNORE INTO users (username, password, role, name, subjects, class, school) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('student', hash_password('student123'), 'student', 'Студент', '["python", "math", "programming"]', '10А', 'Школа №1 г. Мирный')
        )

        # Демо-тесты
        if db.execute('SELECT COUNT(*) FROM tests').fetchone()[0] == 0:
            test_id = db.execute(
                'INSERT INTO tests (title, description, difficulty, color, time, questions_count, created_by, subject, is_custom) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                ('🐍 ЛЕГКИЙ ТЕСТ PYTHON - 10 ВОПРОСОВ', 'Основные концепции Python', 'easy', '#4ecdc4', '10-15 минут', 5, 'teacher', 'python', 0)
            ).lastrowid
            questions = [
                ('Какая команда выводит текст в консоль?', 'print()', 'echo()', 'output()', 'console.log()', 'print()', 1),
                ('Как создать список в Python?', 'list = []', 'list = {}', 'list = ()', 'list = <>', 'list = []', 2),
                ('Какой оператор используется для сравнения на равенство?', '=', '==', '===', 'equals', '==', 3),
                ('Как объявить функцию в Python?', 'function my_func():', 'def my_func():', 'func my_func():', 'define my_func():', 'def my_func():', 4),
                ('Что выведет: print(2 ** 3)?', '6', '8', '9', '23', '8', 5)
            ]
            for q in questions:
                db.execute(
                    'INSERT INTO questions (test_id, question_text, option1, option2, option3, option4, correct_answer, question_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (test_id, q[0], q[1], q[2], q[3], q[4], q[5], q[6])
                )
            db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db: db.close()

# --- MANAGERS ---
class UserManager:
    def verify_user(self, u, p):
        user = get_db().execute('SELECT 1 FROM users WHERE username = ? AND password = ?', (u, hash_password(p))).fetchone()
        return bool(user)
    def get_user_role(self, u):
        row = get_db().execute('SELECT role FROM users WHERE username = ?', (u,)).fetchone()
        return row['role'] if row else None
    def create_user(self, u, p, r, n, s=None, c=None, sch=None):
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password, role, name, subjects, class, school) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (u, hash_password(p), r, n, json.dumps(s or []), c, sch))
            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    def get_user_subjects(self, u):
        row = get_db().execute('SELECT subjects FROM users WHERE username = ?', (u,)).fetchone()
        return json.loads(row['subjects']) if row and row['subjects'] else []

class PythonQuiz:
    def get_all_tests(self):
        rows = get_db().execute('''
            SELECT t.*, COUNT(q.id) as actual_questions_count 
            FROM tests t LEFT JOIN questions q ON t.id = q.test_id 
            GROUP BY t.id ORDER BY t.is_custom, t.created_at DESC
        ''').fetchall()
        return [dict(r) | {'is_custom': bool(r['is_custom'])} for r in rows]

    def get_test(self, tid):
        db = get_db()
        test = db.execute('SELECT * FROM tests WHERE id = ?', (tid,)).fetchone()
        if not test: return None
        qs = db.execute('SELECT * FROM questions WHERE test_id = ? ORDER BY question_order', (tid,)).fetchall()
        questions = [{'question': q['question_text'], 'options': [q['option1'], q['option2'], q['option3'], q['option4']], 'answer': q['correct_answer']} for q in qs]
        return dict(test) | {'is_custom': bool(test['is_custom']), 'questions': questions}

    def create_test(self, title, questions, difficulty='easy', created_by='teacher', subject='general'):
        db = get_db()
        color = '#4ecdc4' if difficulty == 'easy' else '#8a2be2'
        time_estimate = f'{len(questions) * 1.5}-{len(questions) * 2} минут'
        test_id = db.execute(
            'INSERT INTO tests (title, description, difficulty, color, time, questions_count, created_by, subject, is_custom) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (f'🐍 {title.upper()}', f'Пользовательский тест: {title}', difficulty, color, time_estimate, len(questions), created_by, subject, 1)
        ).lastrowid
        for i, q in enumerate(questions):
            opts = (q['options'] + [''] * 4)[:4]
            db.execute(
                'INSERT INTO questions (test_id, question_text, option1, option2, option3, option4, correct_answer, question_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (test_id, q['question'], *opts, q['answer'], i + 1)
            )
        db.commit()
        return test_id

    def save_test_result(self, u, tid, score, total, answers):
        get_db().execute('INSERT INTO results (username, test_id, score, total, answers_json) VALUES (?, ?, ?, ?, ?)',
                         (u, tid, score, total, json.dumps(answers)))
        get_db().commit()

    def get_user_results(self, u):
        rows = get_db().execute('''
            SELECT r.*, t.title, t.subject 
            FROM results r JOIN tests t ON r.test_id = t.id 
            WHERE r.username = ? ORDER BY r.created_at DESC
        ''', (u,)).fetchall()
        return [dict(r) for r in rows]

# --- INIT DB ---
if not os.path.exists(DATABASE):
    init_db()
else:
    with app.app_context():
        init_db()

user_manager = UserManager()
quiz = PythonQuiz()

# --- HTML TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Python Анкетник - г. Мирный</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #0c0c0c, #1a1a2e, #16213e); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; overflow-x: hidden; position: relative; }
        .pentagon-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -2; opacity: 0.1; }
        .pentagon { position: absolute; width: 120px; height: 120px; background: linear-gradient(45deg, #4ecdc4, #8a2be2); clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%); animation: float 6s ease-in-out infinite; }
        .pentagon:nth-child(1) { top: 10%; left: 5%; animation-delay: 0s; }
        .pentagon:nth-child(2) { top: 20%; right: 10%; animation-delay: -1s; }
        .pentagon:nth-child(3) { bottom: 15%; left: 15%; animation-delay: -2s; }
        .pentagon:nth-child(4) { bottom: 25%; right: 20%; animation-delay: -3s; }
        .pentagon:nth-child(5) { top: 50%; left: 50%; transform: translate(-50%, -50%); animation-delay: -4s; }
        .snake-path { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; opacity: 0.3; }
        .snake { fill: none; stroke: url(#snakeGradient); stroke-width: 2; stroke-dasharray: 10; stroke-dashoffset: 100; animation: snakeMove 3s linear infinite; }
        @keyframes snakeMove { to { stroke-dashoffset: 0; } }
        @keyframes float { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(5deg); } }
        .page { position: absolute; top: 0; left: 0; width: 100%; min-height: 100vh; padding: 20px; display: none; animation: slideIn 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
        .page.active { display: block; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(50px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card { background: rgba(255, 255, 255, 0.1); padding: 50px; border-radius: 25px; margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(20px); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 80px rgba(78, 205, 196, 0.1); position: relative; overflow: hidden; transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
        .card::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent); transition: left 0.6s ease; }
        .card:hover::before { left: 100%; }
        .card:hover { transform: translateY(-10px); box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4), 0 0 120px rgba(78, 205, 196, 0.2); }
        .btn { background: linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(138, 43, 226, 0.2)); color: white; border: 2px solid transparent; border-image: linear-gradient(135deg, #4ecdc4, #8a2be2) 1; padding: 20px 40px; margin: 20px 0; border-radius: 15px; cursor: pointer; font-size: 18px; font-weight: 600; display: block; width: 100%; transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94); position: relative; overflow: hidden; text-transform: uppercase; letter-spacing: 1px; }
        .btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent); transition: left 0.8s ease; }
        .btn:hover::before { left: 100%; }
        .btn:hover { background: linear-gradient(135deg, rgba(78, 205, 196, 0.3), rgba(138, 43, 226, 0.3)); transform: translateY(-5px) scale(1.02); box-shadow: 0 15px 30px rgba(78, 205, 196, 0.4), 0 0 60px rgba(138, 43, 226, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.1); letter-spacing: 2px; }
        .btn:active { transform: translateY(-2px) scale(1); }
        .btn-teacher { background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(255, 107, 107, 0.2)); border-image: linear-gradient(135deg, #8a2be2, #ff6b6b) 1; }
        .btn-teacher:hover { background: linear-gradient(135deg, rgba(138, 43, 226, 0.3), rgba(255, 107, 107, 0.3)); box-shadow: 0 15px 30px rgba(138, 43, 226, 0.4), 0 0 60px rgba(255, 107, 107, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.1); }
        .user-info { position: fixed; top: 25px; right: 25px; background: rgba(255, 255, 255, 0.15); padding: 15px 25px; border-radius: 15px; backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); z-index: 1000; font-size: 14px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); animation: slideInRight 0.6s ease; }
        @keyframes slideInRight { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .test-card { background: rgba(255, 255, 255, 0.08); padding: 30px; margin: 25px 0; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px); transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); position: relative; overflow: hidden; }
        .test-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #4ecdc4, #8a2be2); transform: scaleX(0); transition: transform 0.4s ease; }
        .test-card:hover::before { transform: scaleX(1); }
        .test-card:hover { background: rgba(255, 255, 255, 0.12); transform: translateY(-8px) scale(1.02); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 60px rgba(78, 205, 196, 0.1); }
        .option { background: rgba(255, 255, 255, 0.08); padding: 20px; margin: 12px 0; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2); transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94); cursor: pointer; position: relative; overflow: hidden; }
        .option::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent); transition: left 0.5s ease; }
        .option:hover::before { left: 100%; }
        .option:hover { background: rgba(255, 255, 255, 0.12); border-color: #4ecdc4; transform: translateX(10px); box-shadow: 0 10px 25px rgba(78, 205, 196, 0.2); }
        .option.selected { background: linear-gradient(135deg, rgba(78, 205, 196, 0.25), rgba(138, 43, 226, 0.25)); border-color: #4ecdc4; transform: translateX(15px); box-shadow: 0 15px 30px rgba(78, 205, 196, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.1); }
        input, select, textarea { width: 100%; padding: 18px; margin: 12px 0; border-radius: 12px; border: 2px solid rgba(255, 255, 255, 0.2); background: rgba(255, 255, 255, 0.1); color: white; font-size: 16px; transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); backdrop-filter: blur(10px); }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #4ecdc4; background: rgba(255, 255, 255, 0.15); box-shadow: 0 0 20px rgba(78, 205, 196, 0.3), 0 0 40px rgba(78, 205, 196, 0.1); transform: scale(1.02); }
        h1, h2, h3, h4 { background: linear-gradient(135deg, #4ecdc4, #8a2be2, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 25px; text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); animation: textGlow 3s ease-in-out infinite alternate; }
        @keyframes textGlow { from { text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); } to { text-shadow: 0 5px 25px rgba(78, 205, 196, 0.5); } }
        h1 { font-size: 3.5em; margin-bottom: 40px; font-weight: 800; letter-spacing: 2px; }
        h2 { font-size: 2.5em; font-weight: 700; letter-spacing: 1px; }
        h3 { font-size: 1.8em; font-weight: 600; }
        .notification { position: fixed; top: 25px; left: 50%; transform: translateX(-50%); padding: 20px 35px; background: linear-gradient(135deg, rgba(78, 205, 196, 0.95), rgba(138, 43, 226, 0.95)); color: white; border-radius: 15px; z-index: 2000; animation: notificationSlide 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94); border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3); backdrop-filter: blur(20px); font-weight: 600; text-align: center; }
        @keyframes notificationSlide { from { top: -100px; opacity: 0; } to { top: 25px; opacity: 1; } }
        .progress-bar { width: 100%; height: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 5px; margin: 25px 0; overflow: hidden; box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3); }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #4ecdc4, #8a2be2, #ff6b6b); border-radius: 5px; transition: width 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94); box-shadow: 0 0 20px rgba(78, 205, 196, 0.5), 0 0 40px rgba(138, 43, 226, 0.3); position: relative; overflow: hidden; }
        .progress-fill::after { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent); animation: progressShine 2s infinite; }
        @keyframes progressShine { to { left: 100%; } }
        .test-navigation { display: flex; justify-content: space-between; margin-top: 40px; gap: 20px; }
        .test-navigation .btn { flex: 1; margin: 0; font-size: 16px; padding: 15px 25px; }
        @media (max-width: 768px) {
            .container { padding: 20px 15px; }
            .card { padding: 30px 20px; }
            h1 { font-size: 2.5em; }
            h2 { font-size: 2em; }
            .test-navigation { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="pentagon-bg">
        <div class="pentagon"></div>
        <div class="pentagon"></div>
        <div class="pentagon"></div>
        <div class="pentagon"></div>
        <div class="pentagon"></div>
    </div>
    <svg class="snake-path" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
            <linearGradient id="snakeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#4ecdc4" />
                <stop offset="50%" stop-color="#8a2be2" />
                <stop offset="100%" stop-color="#ff6b6b" />
            </linearGradient>
        </defs>
        <path class="snake" d="M0,20 Q20,0 40,20 T80,20 T120,60 T160,40 T200,80" />
        <path class="snake" d="M100,0 Q80,20 100,40 T140,60 T180,20 T220,40" />
    </svg>

    {% if session.username %}
    <div class="user-info">
        👤 {{ session.username }} ({{ session.role }})
        <button class="btn" onclick="logout()" style="padding: 8px 15px; margin: 8px 0 0 0; font-size: 12px; width: auto;">Выйти</button>
    </div>
    {% endif %}

    {% if not session.username %}
    <div id="login-page" class="page active">
        <div class="container">
            <div class="card">
                <h1>🎓 Python Анкетник</h1>
                <p style="text-align: center; font-size: 1.3em; margin-bottom: 40px; color: #ccc; line-height: 1.6;">
                    Добро пожаловать в образовательную платформу<br>
                    <strong>г. Мирный, Саха (Якутия)</strong>
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px;">
                    <button class="btn" onclick="showPage('login-form-page')">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">🔐</span>
                        Войти в систему
                    </button>
                    <button class="btn btn-teacher" onclick="showPage('registration-page')">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">✨</span>
                        Регистрация
                    </button>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
                    <h3 style="text-align: center; margin-bottom: 20px;">🎮 Демо доступы</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: center;">
                        <div>
                            <strong>👨‍🏫 Учитель</strong><br>
                            Логин: teacher<br>
                            Пароль: teacher123
                        </div>
                        <div>
                            <strong>🎓 Студент</strong><br>
                            Логин: student<br>
                            Пароль: student123
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div id="login-form-page" class="page">
        <div class="container">
            <div class="card">
                <h1>🔐 Вход в систему</h1>
                <input type="text" id="username" placeholder="👤 Введите логин" value="teacher">
                <input type="password" id="password" placeholder="🔒 Введите пароль" value="teacher123">
                <button class="btn" onclick="login()">🚀 Войти в систему</button>
                <button class="btn" onclick="showPage('login-page')" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.3);">⬅️ Назад</button>
            </div>
        </div>
    </div>
    <div id="registration-page" class="page">
        <div class="container">
            <div class="card">
                <h1>✨ Регистрация</h1>
                <div style="margin-bottom: 30px;">
                    <label style="color: #4ecdc4; font-weight: bold; font-size: 1.2em; display: block; margin-bottom: 15px;">👤 Выберите роль:</label>
                    <select id="reg-role" onchange="toggleRegistrationForm()" style="margin-bottom: 25px;">
                        <option value="student">🎓 Ученик</option>
                        <option value="teacher">👨‍🏫 Учитель</option>
                    </select>
                </div>
                <input type="text" id="reg-username" placeholder="👤 Придумайте логин">
                <input type="password" id="reg-password" placeholder="🔒 Придумайте пароль">
                <input type="text" id="reg-name" placeholder="📝 Введите ваше имя и фамилию">
                <div id="student-fields">
                    <select id="reg-school" style="margin-bottom: 20px;">
                        <option value="">🏫 Выберите школу</option>
                        <option value="Школа №1 г. Мирный">Школа №1 г. Мирный</option>
                    </select>
                    <select id="reg-class" style="margin-bottom: 25px;">
                        <option value="">📚 Выберите класс</option>
                        <option value="10А">10А класс</option>
                    </select>
                    <div style="margin-bottom: 20px;">
                        <label style="color: #4ecdc4; font-weight: bold; font-size: 1.2em; display: block; margin-bottom: 15px;">🎯 Основные предметы:</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <label style="display: flex; align-items: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                                <input type="checkbox" value="python" style="margin-right: 10px;"> 🐍 Python
                            </label>
                            <label style="display: flex; align-items: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                                <input type="checkbox" value="math" style="margin-right: 10px;"> 📐 Математика
                            </label>
                        </div>
                    </div>
                </div>
                <div id="teacher-fields" style="display: none;">
                    <input type="text" id="teacher-school" placeholder="🏫 Место работы">
                </div>
                <button class="btn btn-teacher" onclick="register()">🚀 Зарегистрироваться</button>
                <button class="btn" onclick="showPage('login-page')" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.3);">⬅️ Назад</button>
            </div>
        </div>
    </div>
    {% endif %}

    {% if session.username %}
    <div id="main-menu" class="page active">
        <div class="container">
            <div class="card">
                <h1>🎓 Python Анкетник</h1>
                <p style="font-size: 1.4em; margin-bottom: 40px; color: #ccc; text-align: center;">
                    Добро пожаловать, <strong>{{ session.username }}</strong>! 👋<br>
                    <span style="font-size: 0.8em; color: #4ecdc4;">г. Мирный, Саха (Якутия)</span>
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
                    <button class="btn" onclick="showPage('tests-page')">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">📚</span>
                        Выбрать тест
                    </button>
                    {% if session.role == 'teacher' %}
                    <button class="btn btn-teacher" onclick="showPage('create-test-page')">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">✨</span>
                        Создать тест
                    </button>
                    {% else %}
                    <button class="btn" disabled style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.1);">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">🔒</span>
                        Только для учителей
                    </button>
                    {% endif %}
                    <button class="btn" onclick="showPage('results-page')">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">📊</span>
                        Мои результаты
                    </button>
                    <button class="btn" onclick="logout()">
                        <span style="font-size: 2em; display: block; margin-bottom: 10px;">🚪</span>
                        Выйти
                    </button>
                </div>
            </div>
        </div>
    </div>
    <div id="tests-page" class="page">
        <div class="container">
            <div class="card">
                <h2>🎯 Выберите тест</h2>
                <div id="tests-list"></div>
                <button class="btn" onclick="showPage('main-menu')" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.3);">⬅️ Назад в меню</button>
            </div>
        </div>
    </div>
    {% if session.role == 'teacher' %}
    <div id="create-test-page" class="page">
        <div class="container">
            <div class="card">
                <h2>✨ Создать новый тест</h2>
                <input type="text" id="test-title" placeholder="📝 Введите название теста">
                <select id="test-difficulty">
                    <option value="easy">🐍 Легкий уровень</option>
                    <option value="hard">🔥 Сложный уровень</option>
                </select>
                <!-- Предмет убран -->
                <input type="hidden" id="test-subject" value="general">
                <div id="questions-container"></div>
                <button class="btn" onclick="addQuestion()">➕ Добавить вопрос</button>
                <div style="display: flex; gap: 20px; margin-top: 30px;">
                    <button class="btn btn-teacher" onclick="createTest()" style="flex: 2;">🚀 Создать тест</button>
                    <button class="btn" onclick="showPage('main-menu')" style="flex: 1; background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.3);">❌ Отмена</button>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
    <div id="test-page" class="page">
        <div class="container">
            <div class="card">
                <h2 id="test-title-display">📝 Тестирование</h2>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <div id="question-container"></div>
                <div class="test-navigation">
                    <button class="btn" onclick="previousQuestion()" id="prev-btn">⬅️ Назад</button>
                    <button class="btn" onclick="nextQuestion()" id="next-btn">Далее ➡️</button>
                    <button class="btn btn-teacher" onclick="finishTest()" id="finish-btn" style="display: none;">✅ Завершить тест</button>
                </div>
            </div>
        </div>
    </div>
    <div id="results-page" class="page">
        <div class="container">
            <div class="card">
                <h2>📊 Мои результаты</h2>
                <div id="results-list"></div>
                <button class="btn" onclick="showPage('main-menu')" style="background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.3);">⬅️ Назад в меню</button>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        let currentTest = null;
        let currentQuestionIndex = 0;
        let userAnswers = [];
        let testData = null;

        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            if (pageId === 'tests-page') loadTests();
            else if (pageId === 'results-page') showMyResults();
            else if (pageId === 'create-test-page') {
                document.getElementById('questions-container').innerHTML = '';
                addQuestion();
            }
        }

        function showNotification(msg, type = 'success') {
            const n = document.createElement('div');
            n.className = 'notification';
            n.textContent = msg;
            n.style.background = type === 'success' 
                ? 'linear-gradient(135deg, rgba(78, 205, 196, 0.95), rgba(138, 43, 226, 0.95))'
                : 'linear-gradient(135deg, rgba(255, 107, 107, 0.95), rgba(255, 159, 67, 0.95))';
            document.body.appendChild(n);
            setTimeout(() => {
                n.style.animation = 'notificationSlide 0.5s reverse';
                setTimeout(() => n.remove(), 500);
            }, 3000);
        }

        // === НОВАЯ ФУНКЦИЯ ДОБАВЛЕНИЯ ВОПРОСА ===
        function addQuestion() {
            const container = document.getElementById('questions-container');
            const qNum = container.children.length + 1;
            const html = `
                <div class="test-card">
                    <h4>❓ Вопрос ${qNum}</h4>
                    <input type="text" placeholder="Введите вопрос" class="question-text" required>
                    <div style="margin:15px 0;">
                        <label style="display:block;margin-bottom:8px;color:#4ecdc4;">Варианты ответов:</label>
                        <input type="text" placeholder="Вариант A" class="option" style="margin-bottom:8px;" required>
                        <input type="text" placeholder="Вариант B" class="option" style="margin-bottom:8px;" required>
                        <input type="text" placeholder="Вариант C" class="option" style="margin-bottom:8px;">
                        <input type="text" placeholder="Вариант D" class="option">
                    </div>
                    <label style="display:block;margin:15px 0;color:#8a2be2;">Правильный ответ:</label>
                    <select class="correct-answer-select" style="padding:10px;width:100%;background:rgba(255,255,255,0.1);color:white;border-radius:8px;">
                        <option value="">— Выберите —</option>
                        <option value="0">Вариант A</option>
                        <option value="1">Вариант B</option>
                        <option value="2">Вариант C</option>
                        <option value="3">Вариант D</option>
                    </select>
                    <button class="btn" onclick="this.parentElement.remove()" style="background:rgba(255,107,107,0.2);border-color:#ff6b6b;margin-top:15px;">🗑️ Удалить вопрос</button>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        }

        async function createTest() {
            const title = document.getElementById('test-title').value.trim();
            const difficulty = document.getElementById('test-difficulty').value;
            const subject = 'general'; // фиксированный
            if (!title) return showNotification('Введите название теста!', 'error');

            const questions = [];
            for (const el of document.querySelectorAll('#questions-container > .test-card')) {
                const qText = el.querySelector('.question-text').value.trim();
                const opts = [...el.querySelectorAll('.option')].map(i => i.value.trim()).filter(v => v);
                const corrIdx = el.querySelector('.correct-answer-select').value;
                if (!qText) return showNotification('Заполните текст вопроса!', 'error');
                if (corrIdx === '') return showNotification('Выберите правильный ответ!', 'error');
                if (opts.length < 2) return showNotification('Введите хотя бы два варианта!', 'error');
                if (+corrIdx >= opts.length) return showNotification('Правильный ответ вне диапазона!', 'error');
                questions.push({question: qText, options: opts, answer: opts[+corrIdx]});
            }
            if (questions.length === 0) return showNotification('Добавьте вопросы!', 'error');

            try {
                const res = await fetch('/api/create_test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({title, difficulty, questions, subject})
                });
                const r = await res.json();
                if (r.success) {
                    showNotification('Тест создан! 🎉', 'success');
                    setTimeout(() => showPage('main-menu'), 1500);
                } else showNotification('Ошибка: ' + (r.error || '...'), 'error');
            } catch (e) {
                showNotification('Ошибка подключения!', 'error');
            }
        }

        // === ОСТАЛЬНЫЙ JS (без изменений) ===
        function toggleRegistrationForm() {
            const role = document.getElementById('reg-role').value;
            if (role === 'student') {
                document.getElementById('student-fields').style.display = 'block';
                document.getElementById('teacher-fields').style.display = 'none';
            } else {
                document.getElementById('student-fields').style.display = 'none';
                document.getElementById('teacher-fields').style.display = 'block';
            }
        }

        async function register() {
            const username = document.getElementById('reg-username').value;
            const password = document.getElementById('reg-password').value;
            const name = document.getElementById('reg-name').value;
            const role = document.getElementById('reg-role').value;
            if (!username || !password || !name) {
                showNotification('Заполните все обязательные поля!', 'error');
                return;
            }
            let registrationData = {
                username: username,
                password: password,
                role: role,
                name: name
            };
            if (role === 'student') {
                const school = document.getElementById('reg-school').value;
                const class_name = document.getElementById('reg-class').value;
                if (!school) {
                    showNotification('Выберите школу!', 'error');
                    return;
                }
                if (!class_name) {
                    showNotification('Выберите класс!', 'error');
                    return;
                }
                const subjects = [];
                document.querySelectorAll('#student-fields input[type="checkbox"]:checked').forEach(checkbox => {
                    subjects.push(checkbox.value);
                });
                registrationData.school = school;
                registrationData.class_name = class_name;
                registrationData.subjects = subjects;
            } else {
                const teacherSchool = document.getElementById('teacher-school').value;
                if (!teacherSchool) {
                    showNotification('Введите место работы!', 'error');
                    return;
                }
                registrationData.school = teacherSchool;
            }
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(registrationData)
                });
                const result = await response.json();
                if (result.success) {
                    showNotification('Регистрация успешна! 🎉', 'success');
                    setTimeout(() => showPage('login-form-page'), 1500);
                } else {
                    showNotification(result.error || 'Ошибка регистрации!', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения!', 'error');
            }
        }

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            if (!username || !password) {
                showNotification('Введите логин и пароль!', 'error');
                return;
            }
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const result = await response.json();
                if (result.success) {
                    showNotification('Успешный вход! 🎉', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification('Неверный логин или пароль!', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения!', 'error');
            }
        }

        async function logout() {
            await fetch('/api/logout');
            showNotification('До свидания! 👋', 'success');
            setTimeout(() => location.reload(), 1000);
        }

        async function loadTests() {
            try {
                const response = await fetch('/api/get_tests');
                const data = await response.json();
                const testsList = document.getElementById('tests-list');
                testsList.innerHTML = '';
                if (data.tests.length === 0) {
                    testsList.innerHTML = '<p style="text-align: center; color: #ccc; font-size: 1.3em; padding: 40px;">📭 Нет доступных тестов</p>';
                } else {
                    data.tests.forEach(test => {
                        const testCard = document.createElement('div');
                        testCard.className = 'test-card';
                        const difficultyBadge = test.difficulty === 'easy' 
                            ? '<span style="background: #4ecdc4; color: #1a1a2e; padding: 5px 15px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">🐍 ЛЕГКИЙ</span>'
                            : '<span style="background: #8a2be2; color: white; padding: 5px 15px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">🔥 СЛОЖНЫЙ</span>';
                        testCard.innerHTML = `
                            <h3>${test.title} ${test.is_custom ? '✨' : ''}</h3>
                            <p style="color: #ccc; margin: 15px 0; font-size: 1.1em;">${test.description}</p>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; color: #888; font-size: 0.9em; margin: 20px 0;">
                                <div>📝 Вопросов: ${test.questions_count}</div>
                                <div>${difficultyBadge}</div>
                                <div>⏱ ${test.time}</div>
                            </div>
                            <button class="btn" onclick="startTest(${test.id})" style="margin-top: 10px;">🎯 Начать тест</button>
                        `;
                        testsList.appendChild(testCard);
                    });
                }
            } catch (error) {
                showNotification('Ошибка загрузки тестов!', 'error');
            }
        }

        async function startTest(testId) {
            try {
                const response = await fetch('/api/load_test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test_id: testId})
                });
                const data = await response.json();
                if (data.success) {
                    currentTest = testId;
                    testData = data.test;
                    currentQuestionIndex = 0;
                    userAnswers = new Array(testData.questions.length).fill(null);
                    document.getElementById('test-title-display').textContent = testData.title;
                    showQuestion();
                    showPage('test-page');
                } else {
                    showNotification('Ошибка загрузки теста!', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения!', 'error');
            }
        }

        function showQuestion() {
            const question = testData.questions[currentQuestionIndex];
            const container = document.getElementById('question-container');
            const progress = ((currentQuestionIndex + 1) / testData.questions.length) * 100;
            document.getElementById('progress-fill').style.width = `${progress}%`;
            let html = `<h3 style="margin-bottom: 30px;">${question.question}</h3>`;
            question.options.forEach((option, index) => {
                const isSelected = userAnswers[currentQuestionIndex] === option;
                const escapedOption = option.replace(/'/g, "\\'").replace(/"/g, '\\"');
                html += `<div class="option ${isSelected ? 'selected' : ''}" 
                         onclick="selectAnswer('${escapedOption}')">
                         <span style="font-weight: bold; margin-right: 10px;">${String.fromCharCode(65 + index)}.</span> ${option}
                         </div>`;
            });
            container.innerHTML = html;
            document.getElementById('prev-btn').style.display = currentQuestionIndex > 0 ? 'block' : 'none';
            document.getElementById('next-btn').style.display = currentQuestionIndex < testData.questions.length - 1 ? 'block' : 'none';
            document.getElementById('finish-btn').style.display = currentQuestionIndex === testData.questions.length - 1 ? 'block' : 'none';
        }

        function selectAnswer(answer) {
            userAnswers[currentQuestionIndex] = answer;
            showQuestion();
        }

        function nextQuestion() {
            if (currentQuestionIndex < testData.questions.length - 1) {
                currentQuestionIndex++;
                showQuestion();
            }
        }

        function previousQuestion() {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                showQuestion();
            }
        }

        async function finishTest() {
            try {
                const response = await fetch('/api/submit_test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        test_id: currentTest,
                        answers: userAnswers
                    })
                });
                const result = await response.json();
                if (result.success) {
                    showNotification(`Тест завершен! Результат: ${result.score}/${result.total} 🎉`, 'success');
                    setTimeout(() => showPage('results-page'), 1500);
                } else {
                    showNotification('Ошибка сохранения результатов!', 'error');
                }
            } catch (error) {
                showNotification('Ошибка подключения!', 'error');
            }
        }

        async function showMyResults() {
            try {
                const response = await fetch('/api/get_my_results');
                const data = await response.json();
                const resultsList = document.getElementById('results-list');
                resultsList.innerHTML = '';
                if (!data.success || data.results.length === 0) {
                    resultsList.innerHTML = '<p style="text-align: center; color: #ccc; font-size: 1.3em; padding: 40px;">📭 У вас пока нет результатов тестов</p>';
                } else {
                    data.results.forEach(result => {
                        const percentage = Math.round((result.score / result.total) * 100);
                        const resultDiv = document.createElement('div');
                        resultDiv.className = 'test-card';
                        resultDiv.innerHTML = `
                            <h3>📋 ${result.test_title}</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                                <div style="text-align: center;">
                                    <div style="font-size: 2em; color: #4ecdc4; font-weight: bold;">${result.score}/${result.total}</div>
                                    <div style="color: #888;">Правильных ответов</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2em; color: #8a2be2; font-weight: bold;">${percentage}%</div>
                                    <div style="color: #888;">Результат</div>
                                </div>
                            </div>
                            <div style="color: #ccc; text-align: center;">
                                <div>📚 ${result.subject}</div>
                                <div>🕐 ${result.timestamp}</div>
                            </div>
                        `;
                        resultsList.appendChild(resultDiv);
                    });
                }
            } catch (error) {
                showNotification('Ошибка загрузки результатов!', 'error');
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            {% if session.username %} showPage('main-menu'); {% endif %}
        });
    </script>
</body>
</html>
'''

# --- ROUTES ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    if user_manager.verify_user(data['username'], data['password']):
        session['username'] = data['username']
        session['role'] = user_manager.get_user_role(data['username'])
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/register', methods=['POST'])
def api_register():
    d = request.json
    ok = user_manager.create_user(
        d['username'], d['password'], d['role'], d['name'],
        d.get('subjects'), d.get('class_name'), d.get('school')
    )
    return jsonify({'success': ok}) if ok else jsonify({'success': False, 'error': 'Логин занят'})

@app.route('/api/logout')
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/get_tests')
def api_get_tests():
    # ВСЕ видят ВСЕ тесты — без фильтрации по предметам
    tests = quiz.get_all_tests()
    return jsonify({'tests': tests})

@app.route('/api/load_test', methods=['POST'])
def api_load_test():
    test = quiz.get_test(request.json['test_id'])
    return jsonify({'success': True, 'test': test}) if test else jsonify({'success': False})

@app.route('/api/submit_test', methods=['POST'])
def api_submit_test():
    if 'username' not in session: return jsonify({'success': False, 'error': 'Войдите'})
    d = request.json
    test = quiz.get_test(d['test_id'])
    if not test: return jsonify({'success': False})
    score = sum(1 for i, a in enumerate(d['answers']) if i < len(test['questions']) and a == test['questions'][i]['answer'])
    quiz.save_test_result(session['username'], d['test_id'], score, len(test['questions']), d['answers'])
    return jsonify({'success': True, 'score': score, 'total': len(test['questions'])})

@app.route('/api/create_test', methods=['POST'])
def api_create_test():
    if session.get('role') != 'teacher':
        return jsonify({'success': False, 'error': 'Только для учителей'})
    d = request.json
    try:
        tid = quiz.create_test(d['title'], d['questions'], d['difficulty'], session['username'], 'general')
        return jsonify({'success': True, 'test_id': tid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_my_results')
def api_get_my_results():
    if 'username' not in session: return jsonify({'success': False})
    return jsonify({'success': True, 'results': quiz.get_user_results(session['username'])})

# --- RUN ---
if __name__ == "__main__":
    print("🚀 Сервер запущен: http://localhost:5000")
    print("👨‍🏫 Демо: teacher / teacher123")
    app.run(host='0.0.0.0', port=5000, debug=True)