import hashlib
import json
import sqlite3
from database import get_db


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class UserManager:
    def verify_user(self, username, password):
        user = get_db().execute('SELECT 1 FROM users WHERE username = ? AND password = ?',
                                (username, hash_password(password))).fetchone()
        return bool(user)

    def get_user_role(self, username):
        row = get_db().execute('SELECT role FROM users WHERE username = ?', (username,)).fetchone()
        return row['role'] if row else None

    def create_user(self, username, password, role, name, subjects=None, class_name=None, school=None):
        try:
            db = get_db()
            db.execute('''INSERT INTO users (username, password, role, name, subjects, class, school) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (username, hash_password(password), role, name, json.dumps(subjects or []), class_name, school))
            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_subjects(self, username):
        row = get_db().execute('SELECT subjects FROM users WHERE username = ?', (username,)).fetchone()
        return json.loads(row['subjects']) if row and row['subjects'] else []


class PythonQuiz:
    def get_all_tests(self):
        rows = get_db().execute('''
            SELECT t.*, COUNT(q.id) as actual_questions_count 
            FROM tests t LEFT JOIN questions q ON t.id = q.test_id 
            GROUP BY t.id ORDER BY t.is_custom, t.created_at DESC
        ''').fetchall()
        return [dict(r) | {'is_custom': bool(r['is_custom'])} for r in rows]

    def get_test(self, test_id):
        db = get_db()
        test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
        if not test:
            return None
        questions = db.execute('SELECT * FROM questions WHERE test_id = ? ORDER BY question_order',
                               (test_id,)).fetchall()
        questions_data = [{
            'question': q['question_text'],
            'options': [q['option1'], q['option2'], q['option3'], q['option4']],
            'answer': q['correct_answer']
        } for q in questions]
        return dict(test) | {'is_custom': bool(test['is_custom']), 'questions': questions_data}

    def create_test(self, title, questions, difficulty='easy', created_by='teacher', subject='general'):
        db = get_db()
        color = '#4ecdc4' if difficulty == 'easy' else '#8a2be2'
        time_estimate = f'{len(questions) * 1.5}-{len(questions) * 2} минут'
        test_id = db.execute(
            'INSERT INTO tests (title, description, difficulty, color, time, questions_count, created_by, subject, is_custom) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (f'🐍 {title.upper()}', f'Пользовательский тест: {title}', difficulty, color, time_estimate, len(questions),
             created_by, subject, 1)
        ).lastrowid

        for i, question in enumerate(questions):
            options = (question['options'] + [''] * 4)[:4]
            db.execute(
                'INSERT INTO questions (test_id, question_text, option1, option2, option3, option4, correct_answer, question_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (test_id, question['question'], *options, question['answer'], i + 1)
            )
        db.commit()
        return test_id

    def save_test_result(self, username, test_id, score, total, answers):
        get_db().execute('INSERT INTO results (username, test_id, score, total, answers_json) VALUES (?, ?, ?, ?, ?)',
                         (username, test_id, score, total, json.dumps(answers)))
        get_db().commit()

    def get_user_results(self, username):
        rows = get_db().execute('''
            SELECT r.*, t.title as test_title, t.subject 
            FROM results r JOIN tests t ON r.test_id = t.id 
            WHERE r.username = ? ORDER BY r.created_at DESC
        ''', (username,)).fetchall()
        return [dict(r) for r in rows]


# Создаем экземпляры классов для экспорта
user_manager = UserManager()
quiz = PythonQuiz()