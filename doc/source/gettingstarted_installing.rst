..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Installing Poppy
================

**Note:** These instructions are for running a local instance of Poppy.  We suggest you run this inside a `virtualenv`_.

You must have `CassandraDB`_ installed and running.  We recommend using Docker (see below)


1. From your home folder, create the ``~/.poppy`` folder and clone the repo::

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
    cluster = "localhost"
    keyspace = poppy

4. You need to create the default keyspace "poppy" on your cassandra host/cluster.
   Log into cqlsh, do::

    cqlsh> CREATE KEYSPACE poppy WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;

5. For logging, find the ``[DEFAULT]`` section in
   ``~/.poppy/poppy.conf`` and modify as desired::

    log_file = server.log

6. Change directories back to your local copy of the repo::

    $ cd poppy

7. Run the following command so you can see the results of any changes you
   make to the code without having to reinstall the package each time::

    $ pip install -e .

8. Start the Poppy server::

    $ poppy-server

9. Test that Poppy is working by requesting the home doc (with a sample project ID)::

    $ curl -i -X GET http://0.0.0.0:8888/v1.0/123

   You should get an **HTTP 200** along with some headers that look similar to the following example::

    HTTP/1.0 200 OK
    Date: Thu, 13 Feb 2014 14:34:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 464
    Content-Type: application/json-home
    Cache-Control: max-age=86400

Installing `CassandraDB`_ (using Docker)
------------------------------------------------

1. From the `docker/cassandra` folder::

    $ docker build -t db .

2. Open the 9160 and 9042 ports for Cassandra.
   Name the container 'cassandra'::

    $ docker run -d -p 9160:9160 -p 9042:9042 --name cassandra db

3. Test the running cassandra instance (you may need to ``pip install cqlsh``)::

    $ cqlsh <local ip> 9160

   Where local ip is the ip address of your running docker container


4. Import the schema file from the poppy/storage/cassandra/schema.cql file.

.. _`CassandraDB` : http://cassandra.apache.org
.. _`virtualenv` : https://pypi.python.org/pypi/virtualenv/

