# osm-validator
OSM validator

# Requirements
- python 3.6
- postgres + postgis + hstore
- redis
- osm2pgsql
- osmconvert (osmctools)
- node

# Run tests

    export $(cat .env.test | xargs) && tox

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


### Inside docker ###
# Remove all prev containers (clear system)
    sudo docker rm -f $(sudo docker ps -a -q)

# Once at first start (may need to use sudo):
    # hard way
    sudo chmod +x dockers/web/wait-for-it.sh
    sudo chmod +x dockers/scheduler/wait-for-postgres.sh
    docker pull postgres:9.6
    export $(cat .env | xargs) && docker-compose up -d
    docker exec -t -i postgres-stubb apt-get update
    docker exec -t -i postgres-stubb apt-get install -y postgresql-9.6-postgis-2.3
    docker exec -t -i postgres-stubb apt-get install -y postgresql-contrib-9.6
    docker exec -t -i postgres-stubb psql -U postgres -c "CREATE DATABASE osmvalidatortest;"
    docker exec -t -i postgres-stubb psql -U postgres -d osmvalidatortest -c "CREATE EXTENSION postgis;"
    docker exec -t -i postgres-stubb psql -U postgres -d osmvalidatortest -c "CREATE EXTENSION hstore;"
    docker exec -t -i postgres-stubb psql -U postgres -c "CREATE USER test WITH PASSWORD 'test';"

    docker-compose run scheduler alembic upgrade head
    docker-compose run scheduler python schedule.py

    # easy way
    cd {path_to_project_dir}
    sudo chmod +x dockers/postgres/first-run-prepare.sh
    sh dockers/postgres/first-run-prepare.sh

# Second and more run
    export $(cat .env | xargs) && docker-compose up -d


### Locally ###
# Install front dependencies

    npm install

# Build front application

    node_modules/.bin/webpack

# Migrate

    export $(cat .env | xargs) && alembic upgrade head

# Run validators

    export $(cat .env | xargs) && python schedule.py

# Run web server

    export $(cat .env | xargs) && python main.py

# Add job to cron

    sudo nano /etc/crontab
    add line '0,15,30,45 * * * * root cd {path_to_project_dir} && docker-compose run scheduler python schedule.py'
    service cron restart
