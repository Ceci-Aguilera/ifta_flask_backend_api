#!/usr/bin/env bash
set -e

echo "Waiting for postgres to connect ..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL is active"


flask db init
flask db migrate
flask db upgrade



echo "Postgresql migrations finished"

python app.py