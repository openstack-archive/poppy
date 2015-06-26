Before you begin
----------------

Install Docker-Compose::

    $ sudo pip install -U docker-compose

Warning - never git commit your secret credentials to upstream!


Install the Full Poppy stack (poppy_stack.yml)
---------------------------------------------

1. Create your poppy.conf Configuration file:

    $ cp docker/api/poppy-sample.conf docker/api/poppy.conf

2. Update docker/api/poppy.conf with your secret settings (this file is git-ignored).

3. Build and Run::

    $ docker-compose -f docker/compose/poppy_stack.yml up -d


Running Poppy Locally
-------------------------------------------

During development, you want to run poppy locally, but use dependencies like Zookeeper and Cassandra within a Docker Container.

1. Build and Run::

    $ docker-compose -f dependencies.yml up -d


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/
