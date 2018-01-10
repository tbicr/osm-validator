#!/bin/bash

printf "Waiting for psql to install...\n"

sudo chmod +x dockers/web/wait-for-it.sh
sudo chmod +x dockers/scheduler/wait-for-postgres.sh

sudo docker pull postgres:9.6

docker-compose up -d postgres
sudo docker exec -t -i postgres-stubb apt-get update
sudo docker exec -t -i postgres-stubb apt-get install -y postgresql-9.6-postgis-2.3
sudo docker exec -t -i postgres-stubb apt-get install -y postgresql-contrib-9.6
sudo docker exec -t -i postgres-stubb psql -U postgres -c "CREATE DATABASE osmvalidatortest;"
sudo docker exec -t -i postgres-stubb psql -U postgres -d osmvalidatortest -c "CREATE EXTENSION postgis;"
sudo docker exec -t -i postgres-stubb psql -U postgres -d osmvalidatortest -c "CREATE EXTENSION hstore;"
sudo docker exec -t -i postgres-stubb psql -U postgres -c "CREATE USER test WITH PASSWORD 'test';"

docker-compose up -d redis
docker-compose up -d web

docker-compose run --no-deps --rm scheduler alembic upgrade head
docker-compose run --no-deps --rm scheduler python schedule.py

printf "Complited!\n"
