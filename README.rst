CDN
=======

Content Delivery Network Management as a Service

Note: This is a work in progress and is not currently recommended for production use.

What is CDN
============

Users have come to expect exceptional speed in their applications, websites, and video experiences.  Because of this, using a CDN has become standard for companies, no matter their size.  

CDN will take all the guess work out of the CDN market for our users.  CDN will give them a consistently speedy experience from integrated partners, with an easy to use RESTful API.

Vendor lock-in to a particular CDN provider is removed by abstracting away the plethora of vendor API's available.  This means that a customer only has to integrate with one CDN API, and reap the benefits of using multiple providers.

Your content can be distributed to multiple providers seamlessly instead of just one.

Running performance benchmarks against each configured CDN provider allows you to simply repoint your DNS at the new provider; and with that simple change you can ensure your application is running using the fastest provider at the time.  It will also allow you to handle CDN failures and minimize disruption to your application from CDN outages.


Features
---------

+ Wraps third party CDN provider API's
    - Fastly (http://www.fastly.net)
    - Your CDN here
+ Sends configurations to *n* configured CDN providers
+ Supports multiple backends (CassandraDB recommended)
    - CassandraDB
    - Your DB provider here
+ Openstack Compatable
    - Uses Keystone for authentication
+ Multiple Origins to pull from (including Rackspace Cloud Files)
+ Supports Multiple Domains
+ Custom Caching and TTL rules
+ Set Restrictions on who can access cached content


What CDN is not
----------------------

CDN does not run its own Edge Cache or POP servers.  This is purely a management API to abstract away the myriad of CDN providers on the market.



Getting Started
-------------------------------------------

**Note:** These instructions are for running a local instance of CDN and
not all of these steps are required. It is assumed you have `CassandraDB`
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
   to your local casssandra cluster::

    [drivers:storage:cassandra]
    cluster = "localhost"
    keyspace = cdn

4. By using cassandra storage plugin, you will need to create the default 
   keyspace "cdn" on your cassandra host/cluster. So log into cqlsh, do::
    
    cqlsh> CREATE KEYSPACE cdn WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;

5. For logging, find the ``[DEFAULT]`` section in
   ``~/.cdn/cdn.conf`` and modify as desired::

    log_file = server.log

6. Change directories back to your local copy of the repo::

    $ cd cdn

7. Run the following so you can see the results of any changes you
   make to the code without having to reinstall the package each time::

    $ pip install -e .

8. Start the CDN server::

    $ cdn-server

9. Test out that CDN is working by requesting the home doc::

    $ curl -i -X GET http://0.0.0.0:8888/v1.0

You should get an **HTTP 200** along with some headers that will look
similar to this::

    HTTP/1.0 200 OK
    Date: Thu, 13 Feb 2014 14:34:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 464
    Content-Type: application/json-home
    Cache-Control: max-age=86400


Installing Cassandra Locally
-----------------------------

Mac OSX
-------

1. Update your Java SDK to the latest version (v7+)

    http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html

You can check the version currently running with 
    
    $java -version

2. Follow the instructions on the datastax site to install cassandra for Mac OSX 
    
    http://www.datastax.com/2012/01/working-with-apache-cassandra-on-mac-os-x

3. Import the Cassandra Schema to set up the required tables that CDN will need
    
    Open ./cqlsh and import the /cdn/storage/cassandra/schema.cql file

    
.. _`CassandraDB` : http://cassandra.apache.org
.. _`pyenv` : https://github.com/yyuu/pyenv/
.. _`virtualenv` : https://pypi.python.org/pypi/virtualenv/

