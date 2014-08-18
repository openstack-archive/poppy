API Tests
=========

The API tests
+ test an actual API against a running environment.
+ are black box tests
+ can be used to test any running instance of poppy server (dev, test, prod,
  local instance, containerized instance)


To run the tests
================

1. Install the dependencies::

    pip install -r requirements.txt

2. Run the tests with 'tox' command. By default, the API tests will start a
   poppy server at http://0.0.0.0:8888 against a mock DB.

3. To run API tests against an external server (or a local running instance of
   poppy), you will need to do the following extra steps ::

    a) Set the environment variables CAFE_CONFIG_FILE_PATH,
       CAFE_ROOT_LOG_PATH, CAFE_TEST_LOG_PATH. See example below

        export CAFE_CONFIG_FILE_PATH=~/.poppy/api.conf
        export CAFE_ROOT_LOG_PATH=~/.poppy/logs
        export CAFE_TEST_LOG_PATH=~/.poppy/logs

    b) Copy the api.conf file to the path set by CAFE_CONFIG_FILE_PATH ::

        cp tests/etc/api.conf ~/.poppy/api.conf

    c) Update api.conf with the appropriate values
    d) Run the tests with 'tox' command.
