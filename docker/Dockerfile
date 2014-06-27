# Ensure you have your private key in the folder where this DockerFile is run from
# and upload your public key to the private Github repo

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
RUN cp /home/cdn/etc/cdn.conf /etc/cdn.conf
RUN cp /home/cdn/etc/logging.conf /etc/logging.conf

# Configure Cassandra Storage Driver, and Fastly Provider
RUN sed -i -e"s/cluster = \"localhost\"/cluster = \"0.0.0.0\"/" /etc/cdn.conf
RUN sed -i -e"s/apikey = \"MYAPIKEY\"/apikey = \"deadbeef\"/" /etc/cdn.conf


RUN more /etc/cdn.conf

# Start CDN
EXPOSE 8888
ENTRYPOINT ["cdn-server"]
