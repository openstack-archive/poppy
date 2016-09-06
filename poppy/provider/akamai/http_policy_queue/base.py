# Copyright (c) 2016 Rackspace, Inc.
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
class HttpPolicyQueue(object):
    """Keep track of old HTTP policies for deletion.

    The policy object on queue is used to kick off a task
    that deletes obsolete akamai http policies at pre-defined intervals.
    """

    def __init__(self, conf):
        self._conf = conf

    def enqueue_http_policy(self, http_policy):
        """Add new http policy element to the queue.

        :param http_policy: a new element to add to the queue
        :type http_policy: dict
        """
        raise NotImplementedError

    def dequeue_http_policy(self, consume=True):
        """Remove and return an item from the queue.

        :param consume: if true the policy is removed from the list and
            returned otherwise the policy is retrieved queue
        """
        raise NotImplementedError

    def traverse_queue(self, consume=False):
        """Traverse queue and return all items on the queue in a list"""
        raise NotImplementedError

    def put_queue_data(self, queue_data_list):
        """Clear the queue and put new queue data list in the queue.

        :param queue_data_list: new queue data to replace current queue data
        :type queue_data_list: [dict()] -- list of dictionaries
        """
        raise NotImplementedError
