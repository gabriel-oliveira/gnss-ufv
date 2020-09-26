#!/bin/sh
# wait-for-postgres.sh

set -e

cmd="$@"
  
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - waiting"
  sleep 3
done

>&2 echo "Running server"
exec $cmd
