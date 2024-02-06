# Проект на FastAPI для наложения водяного знака на загруженные изображения.
Позволяет выполнить наложение только для авторизованных пользователей.

В настоящий момент работает без базы данных.
Пользователи "захардкожены": user1;12345 и user2;12345

В дальнейшем планируется добавление базы данных (sqlite/Postgres + SQLAlchemy + alembic) и просмотр полученных файлов (
каждому пользователю только свои).

### Используемый стек:
FastAPI,
jinja2 (для шаблонов простых страниц + Bootstrap),
python-jose (для работы с токенами авторизации),

### Установка:
python -m venv venv
.\venv\Scripts\activate  (Windows)

source venv/bin/activate  (Ubuntu)

pip install -r requirements.txt

python -m uvicorn main:app --reload