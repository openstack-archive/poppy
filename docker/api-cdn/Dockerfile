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

# uwsgi && virtualenv
RUN pip install uwsgi virtualenv

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
RUN git clone git@github.com:tonytan4ever/cdn /home/cdn

# Create a virtual environment
RUN virtualenv /opt/python27

# Install Requirements
RUN sudo /opt/python27/bin/pip install -r /home/cdn/requirements/requirements.txt
# RUN sudo pip install -r /home/cdn/cdn/provider/fastly/requirements.txt
RUN sudo /opt/python27/bin/pip install -e git+https://github.com/zebrafishlabs/fastly-python@b98a756b2a03687d76c3cfa0e024a445af85b38d#egg=fastly-python
RUN sudo /opt/python27/bin/pip install httplib2>=0.8

RUN sudo pip install -e /home/cdn/.

# Set up the configuration files
ADD ./cdn.conf /etc/cdn.conf
ADD ./logging.conf /etc/logging.conf
ADD ./uwsgi.ini /root/uwsgi.ini

RUN more /etc/cdn.conf

# Start CDN
EXPOSE 80
CMD ["/usr/local/bin/uwsgi", "--ini", "/root/uwsgi.ini", "-H", "/opt/python27"]
