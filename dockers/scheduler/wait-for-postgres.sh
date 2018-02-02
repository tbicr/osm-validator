#!/bin/bash

# Wait for the postgres container to finish booting before running whatever

DB_NAME=postgres
DB_PORT=5432

printf "Waiting for postgres to boot..."

for _ in `seq 0 100`; do
    (echo > /dev/tcp/${DB_NAME}/${DB_PORT}) >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        printf " done!\n"
        break
    fi
    printf '.'
    sleep 1
done

exec "$@"