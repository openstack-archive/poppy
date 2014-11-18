#!/usr/bin/env python
# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
import os
import sys

import pip
import setuptools
from setuptools.command.test import test as TestCommand


requirement_files = []
# walk the requirements directory and gather requirement files
for root, dirs, files in os.walk('requirements'):
    for requirements_file in files:
        requirements_file_path = os.path.join(root, requirements_file)
        # parse_requirements() returns generator of requirement objects
        requirement_files.append(
            pip.req.parse_requirements(requirements_file_path))

# parse all requirement files and generate requirements
requirements = set()
for requirement_file in requirement_files:
    requirements.update([str(req.req) for req in requirement_file])
# convert requirements in to list
requirements = list(requirements)


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

setuptools.setup(
    install_requires=requirements,
    setup_requires=['pbr'],
    pbr=True,
    tests_require=['tox'],
    cmdclass={'test': Tox})
