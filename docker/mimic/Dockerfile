##
##    Mimic
##
##

FROM ubuntu:14.04
MAINTAINER Amit Gandhi <amit.gandhi@rackspace.com>

RUN apt-get -qq update
RUN apt-get -qq upgrade

# Install Pip, Python, etc
RUN apt-get -qqy install git-core python-dev wget

# pip
RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
RUN python get-pip.py

# Pull project
RUN git clone https://github.com/malini-kamalambal/mimic.git /home/mimic

# Install Requirements
RUN sudo pip install -r /home/mimic/requirements.txt

# Start Mimic
EXPOSE 8900
CMD export PYTHONPATH=$PYTHONPATH:/home/mimic
CMD ["twistd", "-n", "mimic"]