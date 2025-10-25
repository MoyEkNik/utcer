from flask import Flask
import os
from config import SECRET_KEY, DATABASE
from database import init_db, close_connection
from routes import configure_routes
from models import user_manager, quiz

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Инициализация базы данных
if not os.path.exists(DATABASE):
    init_db(app)
else:
    with app.app_context():
        init_db(app)

# Настройка обработчика закрытия БД
app.teardown_appcontext(close_connection)

# Регистрация маршрутов
configure_routes(app)

if __name__ == "__main__":
    print("🚀 Сервер запущен: http://localhost:5000")
    print("👨‍🏫 Демо: teacher / teacher123")
    app.run(host='0.0.0.0', port=5000, debug=True)