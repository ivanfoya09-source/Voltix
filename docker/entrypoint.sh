#!/bin/sh
set -eu

echo "======================================"
echo " VOLTIX — Starting Django application "
echo "======================================"

# 1. Перевірка Django
echo "Checking Django configuration..."
python manage.py check

# 2. Статичні файли
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Міграції
# Для локального Docker.
# У production можна ввімкнути RUN_MIGRATIONS=True.
if [ "${RUN_MIGRATIONS:-False}" = "True" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# 4. Порт сервера
PORT="${PORT:-8000}"

echo "Starting Gunicorn on port ${PORT}..."

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
