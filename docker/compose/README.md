Before you begin
----------------

Install Docker-Compose::

    $ sudo pip install -U docker-compose

Warning - never git commit your secret credentials to upstream!


Install the Full Poppy stack (poppy_stack.yml)
----------------------------------------------

1. Create your poppy.conf Configuration file:

    $ cp docker/api/poppy-sample.conf docker/api/poppy.conf

2. Update docker/api/poppy.conf with your secret settings (this file is git-ignored).

3. Build and Run::

    $ docker-compose -f docker/compose/poppy_stack.yml up -d


Running Poppy Locally
---------------------

During development, you want to run poppy locally, but use dependencies like Zookeeper and Cassandra within a Docker Container.

1. Build and Run::

    $ docker-compose -f dependencies.yml up -d


Testing
-------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/


Useful Commands
---------------

Kill All Containers:

    $ docker kill $(docker ps -aq)

Remove All Containers:

    $ docker rm $(docker ps -aq)

List All Containers:

    $ docker ps -a

Rebuild Stack:

    $ docker-compose -f docker/compose/poppy_stack.yml build


Known Issues
------------

Docker Cassandra Image:

    Killing the container (docker kill ...) will remove the data, but not the structure.  This will cause issues with schema migration next time you run the container.  It is recommended to remove the container completely (docker rm ...) to restart with a clean slate.

Akamai Driver:

    Interacting with the Akamai API via the egcurl client requires the host to be running with time synced with an NTP server.  Any time skew will cause policy updates to fail with a 'Invalid Timestamp' error.  Restart your docker host (boot2docker) and try again.

