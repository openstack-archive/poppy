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

3. The API tests require a running database (eg cassandra), in order to
run via tox.

4. Copy the api.conf file to the path set by CAFE_CONFIG_FILE_PATH::

    cp tests/etc/endtoend.conf ~/.poppy/endtoend.conf

5. Set pyrax config file ~/.pyrax.cfg (See https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#pyrax-configuration)

6. Once you are ready to run the tests::

    cd tests/endtoend
    nosetests
