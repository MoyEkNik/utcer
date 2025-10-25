# Конфигурационные параметры
SECRET_KEY = 'secret-key-12345'
DATABASE = 'quiz_database.db'

# Субъекты (оставлены для совместимости)
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