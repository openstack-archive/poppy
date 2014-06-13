CDN
=======

Content Delivery Network Management as a Service

Note: This is a work in progress and is not currently recommended for production use.

What is CDN
============

Users have come to expect exceptional speed in their applications, websites, and video experiences.  Because of this, using a CDN has become standard for companies, no matter their size.  

Cloud CDN will take all the guess work out of the CDN market for our users.  CDN will give them a consistently speedy experience from integrated partners, with an easy to use RESTful API.

Vendor lock-in to a particular CDN provider is removed by abstracting away the plethora of vendor API's available.  This means that a customer only has to integrate with one CDN API, and reap the benefits of using multiple providers.

Running performance benchmarks against each integrated CDN provider also then allows you to simply repoint your DNS at the new provider and with that simple change you can ensure your application is running under the best provider at the time.  It will also allow you to handle CDN failures and minimize disruption to your application from CDN outages.


Features
---------

- Wraps third party CDN provider API's
    - Fastly (http://www.fastly.net)
    - Your CDN Here!
- Sends configurations to *n* configured CDN providers
- Supports multiple backends (CassandraDB recommended)
    - CassandraDB
    - Your DB provider here
- Openstack Compatable
    - Uses Keystone for authentication


What Cloud CDN is not
----------------------

Cloud CDN does not run its own Edge Cache or POP servers.  This is purely a management API to abstract away the myriad of CDN providers on the market.



Running a local CDN server with CassandraDB
-------------------------------------------

**Note:** These instructions are for running a local instance of CDN and
not all of these steps are required. It is assumed you have `CassandraDB`_
installed and running.

1. From your home folder create the ``~/.cdn`` folder and clone the repo::

    $ cd
    $ mkdir .cdn
    $ git clone https://github.com/rackerlabs/cdn.git

2. Copy the CDN config files to the directory ``~/.cdn``::

    $ cp cdn/etc/cdn.conf ~/.cdn/cdn.conf
    $ cp cdn/etc/logging.conf ~/.cdn/logging.conf

3. Find the ``[drivers:storage:cassandradb]`` section in
   ``~/.cdn/cdn.conf`` and modify the URI to point
   to your local casssandra instance::

    `TODO`

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

    $ curl -i -X GET http://0.0.0.0:8888/v1

You should get an **HTTP 200** along with some headers that will look
similar to this::

    HTTP/1.0 200 OK
    Date: Thu, 13 Feb 2014 14:34:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 464
    Content-Type: application/json-home
    Cache-Control: max-age=86400


.. _`CassandraDB` : http://cassandra.apache.org
.. _`pyenv` : https://github.com/yyuu/pyenv/
.. _`virtualenv` : https://pypi.python.org/pypi/virtualenv/

