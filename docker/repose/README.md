Based on the Repose Wiki Instructions: https://repose.atlassian.net/wiki/display/REPOSE/Docker


Building the Repose Docker Image
--------------------------------------

From the docker/repose folder:

    $ docker build -t repose_img_1 .


Running the Repose Docker Container
--------------------------------------

Name the container 'repose'

    $ docker run -d -p 80:8080 --name repose repose_img_1

Or with an Interactive Bash Shell::

    $ docker run -t -i -p 80:8080 --name repose repose_img_1 /bin/bash

Other Notes
-----------

The docker container will use the configuration files stored in the "repose_configs" folder.  Please modify these files for your needs.


Currently the following configurations are defined (system-model.cfg)::


Filters
=======

* content-normalization: Blacklists certain headers
* client-auth: Client Authentication (Keystone via the client-auth-n.cfg.xml file)
* api-validator: Role Based Access Control (via the capabilities.wadl.xml file)
* rate-limiting: Control rate of requests to the API (via the rate-limiting.cfg.xml file)


Destinations
============

* Endpoints are passed to the specified host.  A valid destination can either be an endpoint or a target cluster. All nodes within the target cluster of a destination are considered eligible for routing and REPOSE, by default, forwards to each node in round-robin order, starting at the top of the node sequence.
