## Poppy Dockerfile for CI

FROM ubuntu:14.04
MAINTAINER Chris Powell <chris.powell@rackspace.com>

RUN apt-get update && apt-get install -y \
    curl \
    python-dev \
    git

# Get a working version of pip for ubuntu 14.04:
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=744145
RUN /usr/bin/curl -s https://bootstrap.pypa.io/get-pip.py | python

# Seed the initial requirements to make startups faster
ADD ./requirements /root/requirements
RUN pip install -r /root/requirements/requirements.txt

# Pip install uwsgi rather than use the system version
RUN pip install uwsgi

# Set up the configuration files
ADD ./docker/api_ci/poppy.conf /etc/poppy.conf
ADD ./docker/api_ci/logging.conf /etc/logging.conf
ADD ./docker/api_ci/uwsgi.ini /root/uwsgi.ini

# ADD start_poppy script
ADD ./docker/api_ci/start_poppy.sh /root/start_poppy.sh

# create uwsgi log directory
RUN mkdir -p /var/log/poppy && chmod -R +w /var/log/poppy

# create uwsgi pid directory
RUN mkdir -p /var/run/poppy && chmod -R +w /var/run/poppy

EXPOSE 8081
