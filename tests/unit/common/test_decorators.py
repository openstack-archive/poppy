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

from poppy.common import decorators
from tests.unit import base


class LazyPropertyTest(base.TestCase):

    def test_delete(self):
        original_value = object()
        new_value = object()

        class TestClass(object):
            @decorators.lazy_property(write=True)
            def var(self):
                return original_value

        test_class = TestClass()
        setattr(test_class, 'var', new_value)
        self.assertEqual(new_value, test_class.var)

        del test_class.var
        self.assertEqual(original_value, test_class.var)

    def test_set(self):
        original_value = object()
        new_value = object()

        class TestClass(object):
            @decorators.lazy_property(write=True)
            def var(self):
                return original_value

        test_class = TestClass()
        setattr(test_class, 'var', new_value)

        self.assertEqual(new_value, test_class.var)
