Building the Cassandra Docker Image
--------------------------------------

From the docker/cassandra folder:

    $ docker build -t db .




Running the Cassandra Docker Container
--------------------------------------

Open the 9160 and 9042 ports for Cassandra.
Name the container 'cassandra'

    $ docker run -d -p 9160:9160 -p 9042:9042 --name cassandra db


Testing
--------

Access the running cassandra instance (you may need to ``pip install cqlsh``):

    $ cqlsh <local ip> 9160

Where local ip is the ip address of your running docker container


Import Schema
---------------

Import the schema file from the poppy/storage/cassandra/schema.cql file.

