##
##    Poppy
##
##

FROM ubuntu:14.04
MAINTAINER Amit Gandhi <amit.gandhi@rackspace.com>

RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Pip, Python, etc
RUN apt-get -qqy install git-core wget curl libpython-dev libev4 libev-dev libffi6 libffi-dev libssl-dev python-dev

# setuptools
RUN wget https://bootstrap.pypa.io/ez_setup.py
RUN python ez_setup.py

# pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

# uwsgi 
RUN pip install uwsgi 

# Pull project
RUN git clone https://github.com/openstack/poppy.git /home/poppy

# Install Requirements
RUN sudo pip install -r /home/poppy/requirements/requirements.txt

# Install testrepository
RUN sudo pip install testrepository

RUN sudo pip install -e /home/poppy/.

# Set up the configuration files
ADD poppy.conf /etc/poppy.conf
ADD logging.conf /etc/logging.conf
ADD uwsgi.ini /root/uwsgi.ini

# Deploy the startup script
ADD startup.sh /usr/local/bin/poppy_startup
RUN chmod 755 /usr/local/bin/poppy_startup

# create uwsgi log directory
RUN mkdir -p /var/log/poppy
RUN chmod -R +w /var/log/poppy

# create uwsgi pid directory
RUN mkdir -p /var/run/poppy
RUN chmod -R +w /var/run/poppy

# Run the startup script
RUN chmod 755 /usr/local/bin/poppy_startup

EXPOSE 8080

# wait for the cassandra container to initialize before starting up
CMD poppy_startup
