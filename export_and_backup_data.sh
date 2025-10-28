#!/bin/bash

# Скрипт для экспорта данных из SQLite в JSON для последующего импорта в PostgreSQL

echo "=== Экспорт данных из SQLite ==="

python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    -o fixtures/initial_data.json \
    accounts auth contenttypes sessions \
    shop bloggers ads managers reviews payments

echo "✓ Данные экспортированы в fixtures/initial_data.json"
echo "Данные будут автоматически загружены при запуске docker-compose"
