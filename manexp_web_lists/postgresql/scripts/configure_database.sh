#!/usr/bin/env bash

set -Eeuo pipefail

# Configure Docker
./postgresql/scripts/configure_docker.sh

# Configure PostgreSQL
sudo mkdir -p "$POSTGRES_DATA_DIR" # Create custom data dir
sudo chown 999:999 "$POSTGRES_DATA_DIR" # Give this data dir to postgres user
sudo chmod 700 "$POSTGRES_DATA_DIR" # Change permissions

cd ./postgresql/docker || exit # Go to docker folder

sudo docker compose --env-file "../../../.env" up -d # Run docker

CONTAINER_NAME="docker-database-1"

sudo docker exec \
    -e PIPELINE_USER="$POSTGRES_PIPELINE_USER" \
    -e PIPELINE_PASSWORD="$POSTGRES_PIPELINE_PASSWORD" \
    "$CONTAINER_NAME" \
    psql \
        -U "$POSTGRES_ADMIN_USER" \
        -d "$POSTGRES_DB" \
        -v ON_ERROR_STOP=1 \
        -c "
            DO \$\$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM pg_roles
                    WHERE rolname = '$POSTGRES_PIPELINE_USER'
                ) THEN
                    CREATE ROLE $POSTGRES_PIPELINE_USER
                        LOGIN
                        PASSWORD '$POSTGRES_PIPELINE_PASSWORD'
                        NOSUPERUSER
                        NOCREATEDB
                        NOCREATEROLE
                        NOINHERIT;
                END IF;
            END
            \$\$;

            CREATE SCHEMA IF NOT EXISTS products
                AUTHORIZATION $POSTGRES_PIPELINE_USER;

            CREATE SCHEMA IF NOT EXISTS seeds
                AUTHORIZATION $POSTGRES_PIPELINE_USER;

            ALTER SCHEMA products
                OWNER TO $POSTGRES_PIPELINE_USER;

            ALTER SCHEMA seeds
                OWNER TO $POSTGRES_PIPELINE_USER;

            ALTER ROLE $POSTGRES_PIPELINE_USER
                SET search_path = products, seeds;
        " # Create pipeline user and make a schema for it
