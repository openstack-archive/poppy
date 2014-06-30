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

# Make ssh dir
RUN mkdir /root/.ssh/

# Copy over private key, and set permissions
ADD docker_rsa /root/.ssh/id_rsa

RUN chmod 700 /root/.ssh/id_rsa
RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config
RUN echo "IdentityFile ~/.ssh/id_rsa" >> /etc/ssh/ssh_config

# Create known_hosts
RUN touch /root/.ssh/known_hosts

# Pull project
RUN git clone git@github.com:rackerlab/cdn /home/cdn

# Install Requirements
RUN sudo pip install -r /home/cdn/requirements/requirements.txt

RUN sudo pip install -e /home/cdn/.

# Set up the configuration files
ADD ./cdn.conf /etc/cdn.conf
ADD ./logging.conf /etc/logging.conf
ADD ./uwsgi.ini /root/uwsgi.ini

# create uwsgi log directory
RUN mkdir -p /var/log/cdn
RUN chmod -R +w /var/log/cdn

# create uwsgi pid directory
RUN mkdir -p /var/run/cdn
RUN chmod -R +w /var/run/cdn

#RUN /usr/local/bin/uwsgi --ini /root/uwsgi.ini

# Start CDN
EXPOSE 80
CMD ["/usr/local/bin/uwsgi", "--ini", "/root/uwsgi.ini"]
