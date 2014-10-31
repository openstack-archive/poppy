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

import uuid

import ddt

from poppy.model.helpers import cachingrule
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import restriction
from poppy.model import service
from tests.unit import base


@ddt.ddt
class TestServiceModel(base.TestCase):

    def setUp(self):
        super(TestServiceModel, self).setUp()

        self.service_name = uuid.uuid1()
        self.flavor_ref = "strawberry"

        self.myorigins = []
        self.mydomains = []
        self.myrestrictions = []
        self.mycaching = []

        self.myorigins.append(origin.Origin('mysite.com'))
        self.myorigins.append(origin.Origin('yoursite.io', port=80, ssl=True))

        self.mydomains.append(domain.Domain('oursite.org'))
        self.mydomains.append(domain.Domain('wiki.cc'))

        self.myrestrictions.append(restriction.Restriction('referrer_site'))
        self.myrestrictions.append(restriction.Restriction('client_ip'))

        self.mycaching.append(cachingrule.CachingRule('images', 3600))
        self.mycaching.append(cachingrule.CachingRule('js', 7200))

    def test_create(self):
        myservice = service.Service(
            self.service_name, self.mydomains, self.myorigins, self.flavor_ref,
            self.mycaching, self.myrestrictions)

        # test all properties
        # name
        self.assertEqual(myservice.name, self.service_name)
        changed_service_name = 'ChangedServiceName'
        myservice.name = changed_service_name
        self.assertEqual(myservice.name, changed_service_name)

        # flavor_ref
        # self.assertEqual(myservice.flavor_ref, self.flavor_ref)

        # domains
        self.assertEqual(myservice.domains, self.mydomains)
        myservice.domains = []
        self.assertEqual(myservice.domains, [])

        # origins
        self.assertEqual(myservice.origins, self.myorigins)
        myservice.origins = []
        self.assertEqual(myservice.origins, [])

        # flavor_ref
        self.assertEqual(myservice.flavor_ref, self.flavor_ref)
        myservice.flavor_ref = "standard"
        self.assertEqual(myservice.flavor_ref, "standard")

        self.assertEqual(myservice.restrictions, self.myrestrictions)
        myservice.restrictions = []
        self.assertEqual(myservice.restrictions, [])

        # caching rules
        self.assertEqual(myservice.caching, self.mycaching)
        myservice.caching = []
        self.assertEqual(myservice.caching, [])

        # status
        self.assertEqual(myservice.status, u'create_in_progress')

    def test_init_from_dict_method(self):
        # this should generate a service copy from my service
        myservice = service.Service(
            self.service_name, self.mydomains, self.myorigins, self.flavor_ref,
            self.mycaching, self.myrestrictions)
        cloned_service = service.Service.init_from_dict(myservice.to_dict())

        self.assertEqual(cloned_service.domains, myservice.domains)
        self.assertEqual(cloned_service.origins, myservice.origins)
        self.assertEqual(cloned_service.flavor_ref, myservice.flavor_ref)

    @ddt.data(u'', u'apple')
    def test_set_invalid_status(self, status):
        myservice = service.Service(
            self.service_name,
            self.mydomains,
            self.myorigins,
            self.flavor_ref)

        self.assertRaises(ValueError, setattr, myservice, 'status', status)

    @ddt.data(u'create_in_progress', u'deployed', u'delete_in_progress')
    def test_set_valid_status(self, status):
        myservice = service.Service(
            self.service_name,
            self.mydomains,
            self.myorigins,
            self.flavor_ref)

        myservice.status = status

        self.assertEqual(myservice.status, status)
