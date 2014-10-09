Benchmark Tests
=========

The bennchmark tests use Locust.
See http://docs.locust.io/en/latest/ for more info.


To run the tests
================

1. Install the dependencies::

    pip install -r benchmark-requirements.txt


2. Run the tests::

    cd tests/benchmark
    locust -f poppy-bench.py
    Start the tests from http://localhost:8089/
