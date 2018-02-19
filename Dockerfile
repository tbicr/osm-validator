FROM ubuntu:16.04

ENV LC_ALL=C.UTF-8
ENV LANG C.UTF-8

# update os
RUN apt-get -yqq update --fix-missing
RUN apt-get install -y --no-install-recommends net-tools curl software-properties-common

# install dependencies
RUN apt-get install -y --no-install-recommends osm2pgsql osmctools

# install python3
RUN add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -q -y --no-install-recommends \
        python3.6 python3.6-dev python3-pip python3-setuptools python3-wheel gcc

# install nodejs, npm
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash
RUN apt-get install -y nodejs

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# init app
RUN mkdir /app
WORKDIR /app

# common
COPY osm_validator/ /app/osm_validator/
COPY main.py /app/main.py
COPY schedule.py /app/schedule.py
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
COPY osm2pgslq.style /app/osm2pgslq.style

# migrations
COPY migrations /app/migrations/
COPY alembic.ini /app/alembic.ini

# static
COPY osm_validator_front/ /app/osm_validator_front/
COPY static/ /app/static/
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
COPY webpack.config.js /app/webpack.config.js
COPY .babelrc /app/.babelrc
COPY .eslintrc /app/.eslintrc

# install python requirements
RUN pip3 install pipenv --upgrade
RUN pipenv install --python python3.6

# build js app
RUN npm install
RUN node_modules/.bin/webpack

CMD ["/bin/bash"]
