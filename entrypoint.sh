#!/bin/sh

echo "Starting Django application..."
cd /app

# Wait for PostgreSQL
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done

echo "PostgreSQL is available."

# Run migrations (skip makemigrations in production)
echo "Running database migrations..."
python manage.py migrate --noinput

# Skip collectstatic in development (files are mounted via volume)
# Uncomment for production:
# echo "Collecting static files..."
# python manage.py collectstatic --noinput --clear

echo "Django application is ready!"

# Run the main container command
exec "$@"