CDN
=======

CDN Service_

Running a local CDN server with MongoDB
-------------------------------------------

**Note:** These instructions are for running a local instance of CDN and
not all of these steps are required. It is assumed you have `MongoDB`_
installed and running.

1. From your home folder create the ``~/.cdn`` folder and clone the repo::

    $ cd
    $ mkdir .cdn
    $ git clone https://github.com/rackerlabs/cdn.git

2. Copy the CDN config files to the directory ``~/.cdn``::

    $ cp cdn/etc/cdn.conf-sample ~/.cdn/cdn.conf
    $ cp cdn/etc/logging.conf-sample ~/.cdn/logging.conf

3. Find the ``[drivers:storage:mongodb]`` section in
   ``~/.marconi/marconi.conf`` and modify the URI to point
   to your local mongod instance::

    uri = mongodb://$MONGODB_HOST:$MONGODB_PORT

4. For logging, find the ``[DEFAULT]`` section in
   ``~/.cdn/cdn.conf`` and modify as desired::

    log_file = server.log

5. Change directories back to your local copy of the repo::

    $ cd cdn

6. Run the following so you can see the results of any changes you
   make to the code without having to reinstall the package each time::

    $ pip install -e .

7. Start the CDN server::

    $ cdn-server

8. Test out that CDN is working by requesting the home doc::

    $ curl -i -X GET http://127.0.0.1:8888/v1/

You should get an **HTTP 201** along with some headers that will look
similar to this::

    HTTP/1.0 201 Created
    Date: Fri, 25 Oct 2013 15:34:37 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 0
    Location: /v1/queues/samplequeue


.. _`OpenStack` : http://openstack.org/
.. _`MongoDB` : http://docs.mongodb.org/manual/installation/
.. _`pyenv` : https://github.com/yyuu/pyenv/
.. _`virtualenv` : https://pypi.python.org/pypi/virtualenv/

