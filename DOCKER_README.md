# Запуск приложения через Docker

## Быстрый старт

### 1. Экспорт существующих данных (опционально)

Если у вас уже есть данные в SQLite и вы хотите их сохранить:

```bash
./export_and_backup_data.sh
```

Это создаст файл `fixtures/initial_data.json` с вашими данными.

### 2. Запуск через Docker Compose

```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Или в фоне
docker-compose up -d --build
```

### 3. Остановка

```bash
# Остановка контейнеров
docker-compose down

# Остановка с удалением данных
docker-compose down -v
```

## Структура Docker

- **db** - PostgreSQL база данных
- **web** - Django приложение
- Данные сохраняются в volumes для восстановления

## Доступ к приложению

После запуска приложение доступно по адресу:
- **Приложение**: http://localhost:8000/
- **Админ-панель**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## Учетные записи

После запуска создаются следующие пользователи:

**Администратор:**
- Email: admin@gmail.com
- Пароль: admin12345

**Менеджер:**
- Email: manager@gmail.com  
- Пароль: manager12345

**Пользователь:**
- Email: user@gmail.com
- Пароль: user12345

## Работа с базой данных

```bash
# Подключение к PostgreSQL в контейнере
docker-compose exec db psql -U sanderstu -d sanderstu

# Django shell
docker-compose exec web python manage.py shell

# Миграции
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## Сохранение данных

Данные PostgreSQL сохраняются в Docker volume `postgres_data`. Для полного бэкапа:

```bash
# Экспорт данных
docker-compose exec db pg_dump -U sanderstu sanderstu > backup.sql

# Восстановление данных
cat backup.sql | docker-compose exec -T db psql -U sanderstu sanderstu
```

## Переменные окружения

Для изменения настроек отредактируйте `docker-compose.yml`:

- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `DEBUG` - режим отладки Django

## Troubleshooting

### Проблемы с миграциями

```bash
# Полная пересборка миграций
docker-compose down -v
docker-compose up --build
```

### Логи контейнеров

```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs web
docker-compose logs db
```

### Пересоздание БД

```bash
docker-compose down -v  # Удалить volumes
docker-compose up --build
```

## Локальная разработка (без Docker)

Для запуска локально без Docker:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Создание данных
python manage.py seed_data

# Запуск сервера
python manage.py runserver
```

При локальном запуске используется SQLite.
