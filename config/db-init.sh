#!/bin/sh

set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

echo "create database $PG_DATABASE"
"${psql[@]}" <<-EOSQL
    CREATE DATABASE $PG_DATABASE;
EOSQL

echo "loading HStore and PostGIS extensions into $PG_DATABASE"
"${psql[@]}" --dbname="$PG_DATABASE" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS hstore;
    CREATE EXTENSION IF NOT EXISTS postgis;
EOSQL
