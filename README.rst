Poppy
=======

CDN as a Service

What is Poppy
============

Users have come to expect exceptional speed in their applications, websites, and video experiences.  Because of this, using a CDN has become standard for companies, no matter their size.

Poppy will take all the guess work out of the CDN market for our users.  Poppy will give them a consistently speedy experience from integrated partners, with an easy to use RESTful API.

Vendor lock-in to a particular CDN provider is removed by abstracting away the plethora of vendor API's available.  This means that a customer only has to integrate with one CDN API, and reap the benefits of using multiple providers.

Your content can be distributed to multiple providers seamlessly instead of just one.

Running performance benchmarks against each configured CDN provider allows you to simply repoint your DNS at the new provider; and with that simple change you can ensure your application is running using the fastest provider at the time.  It will also allow you to handle CDN failures and minimize disruption to your application from CDN outages.


Features
---------

+ Wraps third party CDN provider API's
    - Akamai (Production Ready)
    - Fastly (In Development)
    - Amazon CloudFront (In Development)
    - MaxCDN (In Development)
    - Your CDN Here...
+ Sends configurations to *n* configured CDN providers
+ Supports multiple backends (CassandraDB recommended)
    - CassandraDB
    - Your DB provider here
+ Supports multiple dns providers
    - Rackspace DNS
    - Openstack Designate (Coming Soon)
+ Openstack Compatable
    - Uses Keystone for authentication
    - Uses Swift for log delivery
+ Multiple Origins to pull from (Public Servers, Amazon S3 Buckets, ...)
+ Supports Multiple Domains
+ Custom Caching and TTL rules
+ Set Restrictions on who can access cached content


What Poppy is not
----------------------

Poppy does not run its own Edge Cache or POP servers.  This is purely a management API to abstract away the myriad of CDN providers on the market.



Getting Started
-------------------------------------------

**Note:** These instructions are for running a local instance of CDN and
not all of these steps are required. It is assumed you have `CassandraDB` and `Zookeeper`
installed and running in a Docker Container.

1. From your home folder create the ``~/.poppy`` folder and clone the repo::

    $ cd
    $ mkdir .poppy
    $ git clone https://github.com/openstack/poppy.git

2. Copy the Poppy config files to the directory ``~/.poppy``::

    $ cp poppy/etc/poppy.conf ~/.poppy/poppy.conf
    $ cp poppy/etc/logging.conf ~/.poppy/logging.conf

3. Find the ``[drivers:storage:cassandradb]`` section in
   ``~/.poppy/poppy.conf`` and modify the URI to point
   to your local casssandra cluster::

    [drivers:storage:cassandra]
    cluster = <docker ip>
    keyspace = poppy
    migrations_path = /home/poppy/poppy/storage/cassandra/migrations
    automatic_schema_migration = True     #True is recommended for local dev machine


5. For logging, find the ``[DEFAULT]`` section in
   ``~/.poppy/poppy.conf`` and modify as desired::

    log_file = server.log

6. Change directories back to your local copy of the repo::

    $ cd poppy


7. Install general requirements::

    $ pip install -r requirements/requirements.txt

   Run the following so you can see the results of any changes you
   make to the code without having to reinstall the package each time::

    $ pip install -e .

  To install additional dependencies, see `Additional Dependencies`_.


8. Install and start cassandra and zookeeper driver::

    $ pip install docker-compose
    $ docker-compose -f docker/compose/dependencies.yml up -d

9. Start poppy task flow worker::

    $ poppy-worker

10. Start the Poppy server::

    $ poppy-server

11. Test out that Poppy is working by requesting the home doc (with a sample project ID)::

    $ curl -i -X GET -H "X-Project-ID: 000" -H "X-Auth-Token: 000" -H "Content-Type: application/json" http://127.0.0.1:8888/v1.0/

You should get an **HTTP 200** along with some headers that will look
similar to this::

    HTTP/1.0 200 OK
    Date: Thu, 13 Feb 2014 14:34:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 464
    Content-Type: application/json-home
    Cache-Control: max-age=86400

12. To run unit/functional test::

    $ tox

To run a full test suite with api test, you will need to put in correct
CDN vendor configuration (in ``~/.poppy/poppy.conf``) first, e.g::

    [drivers:provider:fastly]
    apikey = "<your_fastly_api_key>"

Then start a poppy server::

    $ poppy-server -v

 And run test suite with api test::

    $ tox -- --exclude=none


Additional Dependencies
-----------------------

Ubuntu 14.04
------------

For Python 2.7::

    $ sudo apt-get install python-dev

For Python 3.4::

    $ sudo apt-get install python3.4-dev

For PyPy::

    $ sudo apt-get install pypy-dev

Install these two packages regardless of the Python version::

    $ sudo apt-get install libffi6 libffi-dev

    $ sudo apt-get install libssl-dev


Installing Cassandra and Zookeeper Locally
------------------------------------------

We recommend running Cassandra and Zookeeper in a docker container when developing locally.

Follow the instuctions in the /poppy/docker/compose/README.md file for running Poppy locally.


Running tests
-----------------------------

First install the additional requirements::

    $ pip install tox

And then run tests::

    $ tox


.. _`CassandraDB` : http://cassandra.apache.org
.. _`pyenv` : https://github.com/yyuu/pyenv/
.. _`virtualenv` : https://pypi.python.org/pypi/virtualenv/
