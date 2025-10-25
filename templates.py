# HTML_TEMPLATE - полный HTML из исходного файла
# Из-за ограничения длины оставлю здесь только заголовок, полный шаблон нужно сохранить отдельно

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Python Анкетник - г. Мирный</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
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