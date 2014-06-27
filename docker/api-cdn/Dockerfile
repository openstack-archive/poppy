##
##    CDN API
##
##

# The following files should exist in this folder before running Dockerfile
# - docker_rsa (private key) -> public key should be published to the private git repo
# - cdn.conf (desired configuration for cdn api)
# - logging.conf (desired logging configuration file)


FROM ubuntu:14.04
MAINTAINER Amit Gandhi <amit.gandhi@rackspace.com>

RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Pip, Python, etc
RUN apt-get -qqy install git-core python-pip curl libpython-dev uwsgi memcached libev4 libev-dev

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
RUN git clone git@github.com:rackerlabs/cdn.git /home/cdn

# Install Requirements
RUN sudo pip install -r /home/cdn/requirements.txt
# RUN sudo pip install -r /home/cdn/cdn/provider/fastly/requirements.txt
RUN sudo pip install -e git+https://github.com/zebrafishlabs/fastly-python@b98a756b2a03687d76c3cfa0e024a445af85b38d#egg=fastly-python
RUN sudo pip install httplib2>=0.8

RUN sudo pip install -e /home/cdn/.

# Set up the configuration files
ADD cdn.conf /etc/cdn.conf
ADD logging.conf /etc/logging.conf

# Start CDN
EXPOSE 8888
ENTRYPOINT ["cdn-server"]
