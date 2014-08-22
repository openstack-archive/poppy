# Copyright (c) 2014 Rackspace Hosting, Inc.
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
import os

tests_dir = os.path.abspath(os.path.dirname(__file__))

if "POPPY_TESTS_CONFIGS_DIR" not in os.environ:
    os.environ["POPPY_TESTS_CONFIGS_DIR"] = os.path.join(tests_dir, "etc")

if "CAFE_CONFIG_FILE_PATH" not in os.environ:
    os.environ["CAFE_CONFIG_FILE_PATH"] = os.path.join(tests_dir,
                                                       "etc/api.conf")

if "CAFE_ROOT_LOG_PATH" not in os.environ:
    os.environ["CAFE_ROOT_LOG_PATH"] = os.path.join(tests_dir, '/logs')

if "CAFE_TEST_LOG_PATH" not in os.environ:
    os.environ["CAFE_TEST_LOG_PATH"] = os.path.join(tests_dir, '/logs')
