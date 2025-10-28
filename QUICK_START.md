# 🚀 Быстрый старт

## Запуск через Docker (рекомендуется)

### 1. Запустить приложение

```bash
docker-compose up --build
```

Приложение будет доступно на http://localhost:8000/

**Остановить:**
```bash
docker-compose down
```

### 2. Войти в систему

**Админ:**
- Email: admin@gmail.com
- Пароль: admin12345

**Менеджер:**
- Email: manager@gmail.com
- Пароль: manager12345

**Пользователь:**
- Email: user@gmail.com
- Пароль: user12345

### 3. Что доступно

- ✅ Автоматическая загрузка данных
- ✅ PostgreSQL база данных
- ✅ Сохранение данных при перезапуске
- ✅ Все зависимости установлены

## Локальная разработка

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Запустить миграции

```bash
python manage.py migrate
python manage.py seed_data
```

### 3. Запустить сервер

```bash
python manage.py runserver
```

## Важные команды

```bash
# Экспорт данных из SQLite
./export_and_backup_data.sh

# Логи Docker
docker-compose logs -f

# Django shell
docker-compose exec web python manage.py shell

# Пересоздать контейнеры
docker-compose down -v && docker-compose up --build
```

## Документация

Подробная документация в `DOCKER_README.md`
