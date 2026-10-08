#!/usr/bin/env bash

set -Eeuo pipefail

if [[ ! -f .env ]]; then
    echo "ERROR: .env file not found" >&2
    exit 1
fi

set -a
source .env
set +a

# Run docker
sudo docker compose up -d database

# Wait for PostgreSQL to become healthy
until sudo docker compose exec -T database \
    pg_isready \
    -U "$POSTGRES_ADMIN_USER" \
    -d "$POSTGRES_DB" \
    >/dev/null 2>&1
do
    sleep 1
done

# Configure PostgreSQL roles and schemas.
#
# The pipeline password is read from the Docker secret inside
# the database container. It never needs to be read by the host
# shell or passed through the command line.
sudo docker compose exec -T \
    -e "PIPELINE_USER=$POSTGRES_PIPELINE_USER" \
    database \
    bash -s <<'BASH'

set -Eeuo pipefail

PIPELINE_PASSWORD="$(< /run/secrets/postgres_pipeline_password)"

export PIPELINE_PASSWORD

psql \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -v ON_ERROR_STOP=1 \
    -v pipeline_user="$PIPELINE_USER" \
    -v pipeline_password="$PIPELINE_PASSWORD" \
    <<'SQL'

SELECT format(
    'CREATE ROLE %I
        LOGIN
        NOSUPERUSER
        NOCREATEDB
        NOCREATEROLE
        NOREPLICATION
        NOBYPASSRLS
        NOINHERIT
        PASSWORD %L',
    :'pipeline_user',
    :'pipeline_password'
)
WHERE NOT EXISTS (
    SELECT FROM pg_roles
    WHERE rolname = :'pipeline_user'
)
\gexec

ALTER ROLE :"pipeline_user"
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    NOBYPASSRLS
    NOINHERIT
    PASSWORD :'pipeline_password';

CREATE SCHEMA IF NOT EXISTS products
    AUTHORIZATION :"pipeline_user";

CREATE SCHEMA IF NOT EXISTS seeds
    AUTHORIZATION :"pipeline_user";

ALTER SCHEMA products
    OWNER TO :"pipeline_user";

ALTER SCHEMA seeds
    OWNER TO :"pipeline_user";

ALTER ROLE :"pipeline_user"
    SET search_path = products, seeds;

SQL

BASH
