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

import inspect
try:
    import ordereddict as collections
except ImportError:
    import collections


class SerializableModel(object):

    """A model mixin class that can serialize itself as JSON."""

    def to_dict(self):
        """Return dict representation of the class."""
        items = [(name, value) for name, value in
                 inspect.getmembers(self, lambda o: not inspect.ismethod(o))
                 if not name.startswith("_")]
        return collections.OrderedDict(items)

    def from_dict(self, attributes):
        """Convert a dictionary into a object.

        Update the current instance based on attribute->value items in
        *attributes* dictionary.
        """
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self
