Before Starting
---------------

The following files should exist in this folder before running Dockerfile
* poppy.conf (desired configuration for poppy api)
* logging.conf (desired logging configuration file)



Building the Poppy Server Docker Image
--------------------------------------

Copy the Dockerfile to the /poppy root folder, then run::

    $ docker build -t poppy .


Running the Poppy Docker Container
--------------------------------------

Name the container 'poppy'::

    $ docker run -d -p 81:8081 --name poppy poppy


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/


Next Steps
----------

If running locally with Cassandra, ensure the Cassandra Docker Container is running and linked.