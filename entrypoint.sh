#!/bin/sh
set -e

echo "Waiting for database..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 2
done

echo "Database is ready"

echo "Running database migrations..."
alembic upgrade head

echo "Running seed script (idempotent)..."
PYTHONPATH=. python scripts/seed_data.py || true

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
