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
except ImportError:        # pragma: no cover
    import collections     # pragma: no cover


class DictSerializableModel(object):

    """A model mixin: class dictionarizable-undictionarizable class mixin.

    A class that can be deserialized from a dictionary and can be serialized
    into a dictionary
    """

    def to_dict(self):
        """Return dict representation (serialize into dictionary) of the class.

        """
        items = [(name, value) for name, value in
                 inspect.getmembers(self, lambda o: not inspect.ismethod(o))
                 if not name.startswith("_")]
        return collections.OrderedDict(items)

    def from_dict(self, attributes):
        """Convert a dictionary into a object/Or copy constructor

        Update the current instance based on attribute->value items in
        *attributes* dictionary.
        """
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self

    @classmethod
    def init_from_dict(cls, input_dict):
        """Construct a model instance from a dictionary.

        This is only meant to be used for converting a
        response model into a model.
        When converting a request-model into a model,
        use to_dict.
        """
        raise NotImplementedError
