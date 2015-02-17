API Tests
=========

The API tests
+ test an actual API against a running environment.
+ are black box tests
+ can be used to test any running instance of poppy server (dev, test, prod, local
  instance, containerized instance)


To run the tests
================

1. Install the dependencies::

    pip install -r requirements.txt

2. Set the following environment variables::

    export CAFE_CONFIG_FILE_PATH=~/.poppy/tests.conf
    export CAFE_ROOT_LOG_PATH=~/.poppy/logs
    export CAFE_TEST_LOG_PATH=~/.poppy/logs

3. Copy the api.conf file to the path set by CAFE_CONFIG_FILE_PATH::

    cp tests/etc/api.conf ~/.poppy/tests.conf

4. Once you are ready to run the tests::

    cd tests/api
    nosetests


Tox Support
-----------

The API tests require cassandra running in your local machine, in order to
run via tox. It is assumed you already have the Cassandra instance up &
running locally. 

You can run tox with a docker container running Cassandra::

This will require docker (or boot2docker for MacOSX) to already be installed on the system.

1. Update your `~/.poppy/tests.conf` to point to your docker cassandra container ip address.
2. Run the `poppy-server` service that the API tests will run against.


Example 1: Run all API tests against a docker hosted cassandra instance::

    tox -e api

Example 2: Run a particular API test function::
    
    tox -e api api/services/test_services.py:TestCreateService -- -m test_create_service_positive


