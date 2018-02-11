# osm-validator
OSM validator

# Configure
- Create `.env` file
- Generate `SECRET_KEY` (`cryptography.fernet.Fernet.generate_key()`)
- Set postgres db connection
- Set redis connection
- Set openstreetmap OAuth credentials (https://wiki.openstreetmap.org/wiki/OAuth):

      OAUTH_OPENSTREETMAP_KEY=Consumer Key there
      OAUTH_OPENSTREETMAP_SECRET=Consumer Secret there

- Set osm initialization dumps:

      OSM_INIT_PBF=http://download.geofabrik.de/europe/belarus-180101.osm.pbf
      OSM_INIT_SEQUENCE_NUMBER=1749
      OSM_CHANGE=http://download.geofabrik.de/europe/belarus-updates/
      OSM_CHECK_TIMEOUT=3600

# Production deploy
Deploy cover database initiation, initial migration, services running.

*NOTE: first run can take some time for initialization*

    git clone git@github.com:tbicr/osm-validator.git
    cd osm-validator
    # setup .env file with Configure section
    export $(cat .env | xargs) && docker-compose up -d

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
