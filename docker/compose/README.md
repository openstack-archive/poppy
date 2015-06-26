Before you begin
----------------

Install Docker-Compose::

    $ sudo pip install -U docker-compose

Update the appropriate compose file being used with the appropriate credentials.

Warning - never git commit your secret credentials to upstream!  We recommend you create a new file named secret.yml (this will be ignored by git) and add your credentials in there.  Reference that file in the -f parameter in the instructions below.


Install the Full Poppy stack (full_stack.yml)
---------------------------------------------

1. Create your poppy.conf Configuration file:

    $ cp docker/api/poppy-sample.conf docker/api/poppy.conf

2. Update docker/api/poppy.conf with your settings.

3. Build and Run::

    $ docker-compose -f full_stack.yml up -d


Running Poppy Locally (local.yml)
-------------------------------------------

During development, you want to run poppy locally, but use dependencies like Zookeeper and Cassandra.

1. Build and Run::

    $ docker-compose -f development.yml up -d


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/
