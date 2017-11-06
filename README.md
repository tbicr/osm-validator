# osm-validator
OSM validator

# Requirements
- postgres
- redis
- python 3.6

# Run tests

    source .env.test && tox

# Migrate

    source .env && alembic upgrade head

# Run server

    source .env && python main.py
