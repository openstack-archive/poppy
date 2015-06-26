# Dockerfile for Repose (www.openrepose.org)

FROM ubuntu

MAINTAINER Damien Johnson (damien.johnson@rackspace.com)

RUN apt-get install -y wget
RUN wget -O - http://repo.openrepose.org/debian/pubkey.gpg | apt-key add - && echo "deb http://repo.openrepose.org/debian stable main" > /etc/apt/sources.list.d/openrepose.list
RUN apt-get update && apt-get install -y repose-valve repose-filter-bundle repose-extensions-filter-bundle

# Remove default Repose configuration files
RUN rm /etc/repose/*.cfg.xml

# Copy our configuration files in.
ADD ./repose_configs/*.cfg.xml /etc/repose/

# Deploy startup script
ADD init.sh /usr/local/bin/repose-docker
RUN chmod 755 /usr/local/bin/repose-docker

# Change this to use other ports for Repose
EXPOSE 8080

# Start Repose
USER root
CMD repose-docker