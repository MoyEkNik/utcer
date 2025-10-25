import sqlite3
import os
import json
from flask import g
from config import DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db(app):
    with app.app_context():
        db = get_db()
        # Создание таблиц
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
        from models import hash_password
        db.execute(
            'INSERT OR IGNORE INTO users (username, password, role, name, subjects) VALUES (?, ?, ?, ?, ?)',
            ('teacher', hash_password('teacher123'), 'teacher', 'Учитель Python', '["python", "informatics"]')
        )
        db.execute(
            'INSERT OR IGNORE INTO users (username, password, role, name, subjects, class, school) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('student', hash_password('student123'), 'student', 'Студент', '["python", "math", "programming"]', '10А', 'Школа №1 г. Мирный')
        )

        # Демо-тест
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

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()