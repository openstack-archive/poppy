API Tests
=========

The API tests
+ test an actual API against a running environment.
+ are black box tests
+ can be used to test any running instance of poppy server (dev, test, prod, local
  instance, containerized instance)


To run the tests
================

1. Create a new virtualenv and install the dependencies::

    NOTE: At the time of this writing opencafe is not compatible with python 3.
          So you will need to create virtualenv with python 2.

    $ pip install -r requirements/requirements.txt
    $ pip install -r tests/test-requirements.txt
    $ pip install -r tests/api/requirements.txt
    $ cafe-config init
    $ cafe-config plugins install http

2. Set the following environment variables::

    export CAFE_CONFIG_FILE_PATH=~/.poppy/tests.conf
    export CAFE_ROOT_LOG_PATH=~/.poppy/logs
    export CAFE_TEST_LOG_PATH=~/.poppy/logs

3. If you desire highlighting in the output, set the following environment variables::

    export NOSE_WITH_OPENSTACK=1
    export NOSE_OPENSTACK_COLOR=1
    export NOSE_OPENSTACK_RED=0.05
    export NOSE_OPENSTACK_YELLOW=0.025
    export NOSE_OPENSTACK_SHOW_ELAPSED=1
    export NOSE_OPENSTACK_STDOUT=1


4. 

a) If you intend to run the tests against a local poppy server,
start server with the following command.

    $ ./run_poppy.sh

b) If you intend to run the tests against a remote poppy server (say test or production env),
grab the url. The url will be in the format
    http://remote.poppy-server.com/v1.0

5. Make a directory ~/.poppy
    mkdir ~/.poppy

6. Copy the api.conf file to the path set by CAFE_CONFIG_FILE_PATH::

    $ cp tests/etc/api.conf ~/.poppy/tests.conf

7. Update the config file in ~/.poppy/tests.conf with the appropriate values

8. Once you are ready to run the tests::

    $ nosetests api


Tox Support
-----------

You can run tox using a docker container hosting Cassandra::

Note - This will require docker (or boot2docker for MacOSX) to already be installed on the system.

1. Update your `~/.poppy/tests.conf` to point to your docker cassandra/zookeeper container ip address.

Example 1: Run all API tests against a docker hosted cassandra instance::

    $ tox -e api

Example 2: Run a particular API test function::

    $ tox -e api api/services/test_services.py:TestCreateService -- -m test_create_service_positive


Mimic Support
-------------

Occassionaly you want to test against a mock api rather than the real thing to get around rate limiting issues,
and to get around having to create accounts with a certain provider.

Mimic helps accomplish this goal for testing.

1.  Run the mimic docker container (via ./run_poppy.sh) and point any remote api url in your test.conf file to your http://dockerhost:8900/mimic_service_name
