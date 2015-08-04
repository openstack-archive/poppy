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

import pip
import setuptools

pip_session = pip.download.PipSession(retries=3)

requirement_files = []
# walk the requirements directory and gather requirement files
for root, dirs, files in os.walk('requirements'):
    for requirements_file in files:
        requirements_file_path = os.path.join(root, requirements_file)
        # parse_requirements() returns generator of requirement objects
        requirement_files.append(
            pip.req.parse_requirements(requirements_file_path,
                                       session=pip_session))

# parse all requirement files and generate requirements
requirements = set()
for requirement_file in requirement_files:
    requirements.update([str(req.req) for req in requirement_file])
# convert requirements in to list
requirements = list(requirements)

setuptools.setup(
    install_requires=requirements,
    setup_requires=['pbr==0.11.0'],
    pbr=True)
