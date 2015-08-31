API Tests
=========

The end to end tests are black box tests, aimed to simulate real world user scenarios.


To run the tests
================

1. Install the dependencies::

    pip install -r requirements.txt
    pip install opencafe

2. Set the following environment variables::

    export CAFE_CONFIG_FILE_PATH=~/.poppy/endtoend.conf
    export CAFE_ROOT_LOG_PATH=~/.poppy/logs
    export CAFE_TEST_LOG_PATH=~/.poppy/logs

3.The end to end tests require a full blown env, setup with real providers and
    database.

4. Copy the endtoend.conf file to the path set by CAFE_CONFIG_FILE_PATH::

    cp tests/etc/endtoend.conf ~/.poppy/endtoend.conf

5. Update the values in endtoend.conf as appropriate.

6. Set pyrax config file ~/.pyrax.cfg::

    Sample contents in a pyrax.cfg file for Rackspace,
    [rackspace_cloud]
    identity_type = keystone
    auth_endpoint = https://identity.api.rackspacecloud.com/v2.0/

   See https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#pyrax-configuration)
   for more details about pyrax configuration.

7. Set up a test origin server in a server with a public IP that the CDN provider
   can pull content from.
   See https://github.com/stackforge/poppy/blob/master/docker/e2e_test/README.md 
   to set up an origin server using docker.

8. Once you are ready to run the tests::

    cd tests/endtoend
    nosetests
