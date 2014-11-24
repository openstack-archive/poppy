
Building the Mimic Docker Image
--------------------------------------

From the docker/api folder::

    $ docker build -t mimic .


Running the Mimic Docker Container
--------------------------------------

Name the container 'mimic::

    $ docker run --restart=no --rm=true -p 8900:8900 mimic


Next Steps
----------

This will expose Mimic on port 8900, so you can access it directly from the host. The default port exposure is intended for communication between containers; see the Docker documentation for more information. If you're using boot2docker, run boot2docker ip to find the right IP.