FROM ubuntu:xenial

ENV LC_ALL=C.UTF-8
ENV LANG C.UTF-8

# update os
RUN apt-get -yqq update --fix-missing
RUN apt-get install -y net-tools

# install dependencies
RUN apt-get install -y git
RUN apt-get install -y osm2pgsql
RUN apt-get install -y osmctools


# install python3
RUN apt-get update \
    && apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -q -y --no-install-recommends python3.6 python3.6-dev python3-pip python3-setuptools python3-wheel gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set python 3.6 as the default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
RUN pip3 install --upgrade pip requests setuptools
RUN pip3 install pipenv

WORKDIR /usr/src/app

COPY Pipfile /usr/src/app/Pipfile
COPY Pipfile.lock /usr/src/app/Pipfile.lock

RUN pipenv install --system
