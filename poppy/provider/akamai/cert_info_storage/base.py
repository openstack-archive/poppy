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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAkamaiSanInfoStorage(object):
    """Interface definition for Akamai Certificate Info Storage.

    """

    def __init__(self, conf):
        self._conf = conf

    @abc.abstractmethod
    def get_cert_info(self, san_cert_name):
        raise NotImplementedError

    @abc.abstractmethod
    def save_cert_last_ids(self, san_cert_name,
                           sps_id_value, job_id_value=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_cert_last_spsid(self, san_cert_name):
        raise NotImplementedError

    @abc.abstractmethod
    def list_all_san_cert_names(self):
        raise NotImplementedError
