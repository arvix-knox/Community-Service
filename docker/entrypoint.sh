#!/bin/sh
set -e

echo "Запуск миграций..."
alembic upgrade head || echo "Миграции пропущены (нет ревизий или ошибка подключения)"

echo "Запуск приложения..."
exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WORKERS_COUNT:-4}" \
    --bind 0.0.0.0:${APP_PORT:-8000} \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
