## Mimic

FROM ubuntu:14.04
MAINTAINER Chris Powell <chris.powell@rackspace.com>

RUN apt-get update && apt-get install -y \
    curl \
    python-dev \
    git

# Get a working version of pip for ubuntu 14.04:
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=744145
RUN /usr/bin/curl -s https://bootstrap.pypa.io/get-pip.py | python

WORKDIR /home/source
RUN git clone https://github.com/rackerlabs/mimic .
RUN pip install -r requirements.txt

EXPOSE 8900
CMD ["twistd", "-n", "mimic"]
