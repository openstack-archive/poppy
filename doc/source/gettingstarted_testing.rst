..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Running tests
=============

First, install the additional requirements using the following command::

    $ pip install tox

Then run tests using the following command::

    $ tox

Tox checks that Poppy works against the following environments::

    python 2.6
    python 2.7
    python 3.3
    pypy

Tox also performs the following coding enforcement checks::

    pep8
    code coverage (100% required)