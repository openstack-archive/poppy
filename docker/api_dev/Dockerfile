##
##    Poppy
##
##

FROM ubuntu:14.04
MAINTAINER Amit Gandhi <amit.gandhi@rackspace.com>

RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Pip, Python, etc
RUN apt-get -qq install git-core wget curl libpython-dev vim memcached libev4 libev-dev python-dev

# setuptools
RUN wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
RUN python ez_setup.py

# pip
RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
RUN python get-pip.py

# uwsgi
RUN pip install uwsgi

# Copy project from local sources
VOLUME /home/poppy
ADD . /home/poppy

# Install Requirements
RUN sudo pip install -r /home/poppy/requirements/requirements.txt

RUN sudo pip install -e /home/poppy/.

# Set up the configuration files
ADD ./docker/api_dev/poppy.conf /etc/poppy.conf
ADD ./docker/api_dev/logging.conf /etc/logging.conf
ADD ./docker/api_dev/uwsgi.ini /root/uwsgi.ini

# Deploy startup script
ADD ./docker/api_dev/init.sh /usr/local/bin/poppy_startup
RUN chmod 755 /usr/local/bin/poppy_startup

# create uwsgi log directory
RUN mkdir -p /var/log/poppy
RUN chmod -R +w /var/log/poppy

# create uwsgi pid directory
RUN mkdir -p /var/run/poppy
RUN chmod -R +w /var/run/poppy

# Start Poppy
EXPOSE 8081
CMD poppy_startup
