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

Coming Soon to a Repo Near You!
