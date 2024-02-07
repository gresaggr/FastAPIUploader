# Проект на FastAPI для наложения водяного знака на загруженные изображения.
Позволяет выполнить наложение только для авторизованных пользователей.

### Используемый стек:
FastAPI,
jinja2 (для шаблонов простых страниц + Bootstrap),
python-jose (для работы с токенами авторизации),

### Установка:
python -m venv venv
.\venv\Scripts\activate  (Windows)

source venv/bin/activate  (Ubuntu)

pip install -r requirements.txt
alembic revision --autogenerate -m 'initial'
alembic upgrade head
python -m uvicorn main:app --reload