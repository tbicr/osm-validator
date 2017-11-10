# osm-validator
OSM validator

# Requirements
- postgres
- redis
- python 3.6

# Run tests

    export $(cat .env.test | xargs) && tox

# Migrate

    export $(cat .env | xargs) && alembic upgrade head

# Run server

    export $(cat .env | xargs) && python main.py
