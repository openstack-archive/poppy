# Dockerfile for Repose (www.openrepose.org)

FROM ubuntu

MAINTAINER Felix Sargent (felix.sargent@rackspace.com)

RUN apt-get update
RUN apt-get install -y wget
RUN wget -O - http://repo.openrepose.org/debian/pubkey.gpg | apt-key add - && echo "deb http://repo.openrepose.org/debian stable main" > /etc/apt/sources.list.d/openrepose.list
RUN apt-get update && apt-get install -y repose-valve repose-filter-bundle repose-extensions-filter-bundle

# Remove default Repose configuration files
RUN rm /etc/repose/*.cfg.xml

# Copy our configuration files in.
COPY ./repose_configs /etc/repose

# Deploy startup script
ADD init.sh /usr/local/bin/repose-docker
RUN chmod 755 /usr/local/bin/repose-docker

# Expose Port 8080 -- Change this to use other ports for Repose
EXPOSE 8080
 
# Start Repose
USER root
CMD repose-docker
