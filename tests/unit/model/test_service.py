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


import ddt

from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model import service

from tests.unit import base


@ddt.ddt
class TestService(base.TestCase):

    def test_create_service(self):
        service_name = 'NewService'
        myorigins = []
        mydomains = []

        myorigins.append(origin.Origin('mysite.com'))
        myorigins.append(origin.Origin('yoursite.io', port=80, ssl=True))

        mydomains.append(domain.Domain('oursite.org'))
        mydomains.append(domain.Domain('wiki.cc'))

        myservice = service.Service(service_name, mydomains, myorigins)

        # test all properties
        # name
        self.assertEqual(myservice.name, service_name)
        self.assertRaises(
            AttributeError, setattr, myservice, 'name', service_name)

        # domains
        self.assertEqual(myservice.domains, mydomains)
        self.assertRaises(AttributeError, setattr, myservice, 'domains', [])

        # origins
        self.assertEqual(myservice.origins, myorigins)
        self.assertRaises(AttributeError, setattr, myservice, 'origins', [])

        # caching, restrictions, and links, empty for now
        self.assertEqual(myservice.caching, [])
        self.assertEqual(myservice.restrictions, [])
        self.assertEqual(myservice.links, [])
