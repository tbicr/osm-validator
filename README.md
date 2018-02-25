# osm-validator
OSM validator

# Configure
- Run `python init_env.py`, read and enter required data (OSM **Consumer Key** and **Consumer Secret**)

*NOTE: Read about openstreetmap OAuth credentials: https://wiki.openstreetmap.org/wiki/OAuth*

*NOTE: You can find `.env` sample in `.env.template` and `.env.test` files*

# Production deploy
Deploy cover database initiation, initial migration, services running.

*NOTE: first run can take some time for initialization*

    git clone git@github.com:tbicr/osm-validator.git
    cd osm-validator
    python3 init_env.py
    docker-compose up -d

# Development
## Requirements
- python 3.6
- postgres + postgis + hstore
- redis
- osm2pgsql
- osmconvert (osmctools)
- nodejs

## Run tests

    export $(cat .env.test | xargs) && tox

## Install front dependencies

    npm install

## Build front application

    node_modules/.bin/webpack

## Migrate

    export $(cat .env | xargs) && alembic upgrade head

## Run validators

    export $(cat .env | xargs) && python schedule.py

## Run web server

    export $(cat .env | xargs) && python main.py
