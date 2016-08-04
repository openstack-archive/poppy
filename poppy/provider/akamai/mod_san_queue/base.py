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
class ModSanQueue(object):
    """Interface definition for Akamai Mod San Queue.

    The purpose of this queue is to buffer the client's
    mod_san request (Currently one request will make one
    san_cert pending, if currently there is no active san
    cert to serve the client request, it is needed to keep
    the request in a queue)

    """

    def __init__(self, conf):
        self._conf = conf

    def enqueue_mod_san_request(self, cert_obj_json):
        raise NotImplementedError

    def dequeue_mod_san_request(self):
        raise NotImplementedError

    def traverse_queue(self):
        """Traverse queue and return all items on the queue in a list."""
        raise NotImplementedError

    def put_queue_data(self, queue_data_list):
        """Juggling and put new queue data list in the queue."""
        raise NotImplementedError

    def move_request_to_top(self):
        raise NotImplementedError
