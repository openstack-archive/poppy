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
import cgi
try:
    import ordereddict as collections
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover


class Model(collections.OrderedDict):

    'response class for rule'

    def __init__(self, rule):
        super(Model, self).__init__()

        if getattr(rule, 'name', None) is not None:
            self['name'] = cgi.escape(rule.name)
        for attr_name in ['http_host', 'http_method',
                          'client_ip', 'request_url',
                          'referrer', 'geography']:
            attr = getattr(rule, attr_name, None)
            if attr is not None:
                self[attr_name] = cgi.escape(attr)
