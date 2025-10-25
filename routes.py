from flask import render_template_string, request, jsonify, session
from models import user_manager, quiz
from templates import HTML_TEMPLATE


def configure_routes(app):
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
        data = request.json
        success = user_manager.create_user(
            data['username'], data['password'], data['role'], data['name'],
            data.get('subjects'), data.get('class_name'), data.get('school')
        )
        return jsonify({'success': success}) if success else jsonify({'success': False, 'error': 'Логин занят'})

    @app.route('/api/logout')
    def api_logout():
        session.clear()
        return jsonify({'success': True})

    @app.route('/api/get_tests')
    def api_get_tests():
        tests = quiz.get_all_tests()
        return jsonify({'tests': tests})

    @app.route('/api/load_test', methods=['POST'])
    def api_load_test():
        test = quiz.get_test(request.json['test_id'])
        return jsonify({'success': True, 'test': test}) if test else jsonify({'success': False})

    @app.route('/api/submit_test', methods=['POST'])
    def api_submit_test():
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Войдите'})

        data = request.json
        test = quiz.get_test(data['test_id'])
        if not test:
            return jsonify({'success': False})

        score = sum(1 for i, answer in enumerate(data['answers'])
                    if i < len(test['questions']) and answer == test['questions'][i]['answer'])

        quiz.save_test_result(session['username'], data['test_id'], score, len(test['questions']), data['answers'])
        return jsonify({'success': True, 'score': score, 'total': len(test['questions'])})

    @app.route('/api/create_test', methods=['POST'])
    def api_create_test():
        if session.get('role') != 'teacher':
            return jsonify({'success': False, 'error': 'Только для учителей'})

        data = request.json
        try:
            test_id = quiz.create_test(data['title'], data['questions'], data['difficulty'], session['username'],
                                       'general')
            return jsonify({'success': True, 'test_id': test_id})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/get_my_results')
    def api_get_my_results():
        if 'username' not in session:
            return jsonify({'success': False})
        return jsonify({'success': True, 'results': quiz.get_user_results(session['username'])})