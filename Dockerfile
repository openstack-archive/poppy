##
##    Poppy
##
##

FROM ubuntu:14.04
MAINTAINER Amit Gandhi <amit.gandhi@rackspace.com>

RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Pip, Python, etc
RUN apt-get -qqy install git-core wget curl libpython-dev vim memcached libev4 libev-dev python-dev

# setuptools
RUN wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
RUN python ez_setup.py

# pip
RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
RUN python get-pip.py

# uwsgi 
RUN pip install uwsgi 

# Pull project
VOLUME /home/poppy
ADD . /home/poppy

# Install Requirements
RUN sudo pip install -r /home/poppy/requirements/requirements.txt

RUN sudo pip install -e /home/poppy/.

# Set up the configuration files
ADD ./docker/api_dev/poppy.conf /etc/poppy.conf
ADD ./docker/api_dev/logging.conf /etc/logging.conf
ADD ./docker/api_dev/uwsgi.ini /root/uwsgi.ini

# create uwsgi log directory
RUN mkdir -p /var/log/poppy
RUN chmod -R +w /var/log/poppy

# create uwsgi pid directory
RUN mkdir -p /var/run/poppy
RUN chmod -R +w /var/run/poppy

#RUN /usr/local/bin/uwsgi --ini /root/uwsgi.ini

# Start Poppy
EXPOSE 8081
CMD ["/usr/local/bin/uwsgi", "--ini", "/root/uwsgi.ini"]
