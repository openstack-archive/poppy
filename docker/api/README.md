Before Starting
---------------

The following files should exist in this folder before running Dockerfile
* poppy.conf (desired configuration for poppy api.  You can make a copy of poppy-sample.conf to get started)
* logging.conf (desired logging configuration file)



Building the Poppy Server Docker Image
--------------------------------------

From the docker/api folder::

    $ docker build -t poppy .


Running the Poppy Docker Container
--------------------------------------

Name the container 'poppy'::

    $ docker run -d -p 80:8080 --name poppy poppy


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/


Next Steps
----------

If running locally with Cassandra, ensure the Cassandra Docker Container is running and linked (see docker-compose instructions).