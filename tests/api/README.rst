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
running locally. You can make the API tests part of tox, by overriding the
default positional argument in tox.ini::
    example : tox -- --exclude=None
