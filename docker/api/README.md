Before Starting
---------------

The following files should exist in this folder before running Dockerfile
* docker_rsa (private key) -> public key should be published to the private git repo
* poppy.conf (desired configuration for poppy api)
* logging.conf (desired logging configuration file)



Building the Poppy Server Docker Image
--------------------------------------

From the docker/api folder::

    $ docker build -t poppy-server .


Running the Poppy Docker Container
--------------------------------------

Name the container 'poppy-server'::

    $ docker run -d -p 81:8081 --name poppy-server poppy-server


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/


Next Steps
----------

If running locally with Cassandra, ensure the Cassandra Docker Container is running and linked.