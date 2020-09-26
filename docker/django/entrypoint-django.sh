#!/bin/sh

set -e

cmd="$@"
  
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - waiting"
  sleep 3
done

>&2 echo "Running migration"
python manage.py makemigrations
python manage.py migrate --noinput

# Manage static files
python manage.py collectstatic --noinput

# Creating superuser
python createsuperuser.py

# Running server
exec $cmd
