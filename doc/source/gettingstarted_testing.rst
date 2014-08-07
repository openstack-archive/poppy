Running Tests
=============

First install the additional requirements::

    $ pip install tox

And then run tests::

    $ tox


Tox will check Poppy works against the following environments::
    
    python 2.6
    python 2.7
    python 3.3
    python 3.4
    pypy


Tox will also perform the following coding enforcement checks::

    pep8
    code coverage (100% required)