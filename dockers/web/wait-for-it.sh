#!/bin/bash

DB_NAME=postgres
DB_PORT=5432

printf "Waiting for psql to boot..."

for _ in `seq 0 100`; do
    (echo > /dev/tcp/${DB_NAME}/${DB_PORT}) >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        printf " Connected!\n"
        break
    fi
    printf '.'
    sleep 1
done

printf "npm install..."
npm install

printf "node_modules/.bin/webpack..."
node_modules/.bin/webpack

printf "pipenv install --system..."
pipenv install --system

printf "python ./main.py..."
python ./main.py

printf "Done"
