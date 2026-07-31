# SkyDesk - Django airline booking system

Учебный Django-проект по ТЗ "Система бронирования авиабилетов".

## Возможности

- модели `Airport`, `Flight`, `Booking`;
- поиск рейсов по городу, названию аэропорта или IATA-коду;
- поиск по дате вылета;
- фильтр по авиакомпании;
- сортировка по времени, цене и количеству свободных мест;
- пагинация списка рейсов;
- форма бронирования с email-валидацией;
- безопасное уменьшение `available_seats` через `transaction.atomic()` и `select_for_update()`;
- Django Messages для успешных и ошибочных действий;
- Django Admin для аэропортов, рейсов и бронирований;
- Bootstrap + custom CSS дизайн.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_flights
python manage.py runserver
```

После запуска откройте:

- сайт: `http://127.0.0.1:8000/`
- админка: `http://127.0.0.1:8000/admin/`

## Структура

```text
flights/
  models.py
  forms.py
  services.py
  views.py
  urls.py
  admin.py
  templates/flights/
  static/flights/css/styles.css
  management/commands/seed_flights.py
```

## Проверка

```bash
python manage.py test flights
python manage.py check
```

## Деплой на Render

1. Создайте новый Web Service на Render из GitHub-репозитория.
2. Выберите Python.
3. В поле Build Command вставьте:

```bash
chmod +x build.sh && ./build.sh
```

4. В поле Start Command вставьте:

```bash
gunicorn config.wsgi:application
```

5. В Environment Variables добавьте:

```text
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1
```

6. Нажмите Create Web Service.

Render сам создаст PostgreSQL-базу данных, если вы используете файл render.yaml из репозитория.
