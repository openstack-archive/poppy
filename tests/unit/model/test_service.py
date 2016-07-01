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
from poppy.model.helpers import rule
from poppy.model import service
from tests.unit import base


@ddt.ddt
class TestServiceModel(base.TestCase):

    def setUp(self):
        super(TestServiceModel, self).setUp()

        self.project_id = str(uuid.uuid4())
        self.service_id = str(uuid.uuid4())
        self.service_name = uuid.uuid1()
        self.flavor_id = "strawberry"

        self.myorigins = []
        self.mydomains = []
        self.myrestrictions = []
        self.mycaching = []
        self.log_delivery = {"enabled": False}

        self.myorigins.append(origin.Origin('mysite.com'))
        self.myorigins.append(origin.Origin('yoursite.io', port=80, ssl=True))

        self.mydomains.append(domain.Domain('oursite.org'))
        self.mydomains.append(domain.Domain('wiki.cc', 'https', 'shared'))

        # test a rule with referrer restriction
        r1 = restriction.Restriction('referrer_site', 'whitelist')
        self.r1_rules = [rule.Rule('referrer_restriction_rule_1')]
        self.r1_rules[0].http_host = 'www.some_bad_site.com'
        r1.rules = self.r1_rules
        self.myrestrictions.append(r1)
        self.myrestrictions.append(restriction.Restriction('client_ip',
                                                           'whitelist'))

        self.mycaching.append(cachingrule.CachingRule('images', 3600))
        self.mycaching.append(cachingrule.CachingRule('js', 7200))

    def test_create(self):
        myservice = service.Service(
            self.service_id,
            self.service_name, self.mydomains, self.myorigins, self.flavor_id,
            self.mycaching, self.myrestrictions, self.log_delivery)

        # test all properties
        # id
        self.assertEqual(myservice.service_id, self.service_id)

        # name
        self.assertEqual(myservice.name, self.service_name)
        changed_service_name = 'ChangedServiceName'
        myservice.name = changed_service_name
        self.assertEqual(myservice.name, changed_service_name)

        # flavor_id
        # self.assertEqual(myservice.flavor_id, self.flavor_id)

        # domains
        self.assertEqual(myservice.domains, self.mydomains)
        self.assertEqual(myservice.domains[0].protocol, 'http')
        self.assertEqual(myservice.domains[1].protocol, 'https')
        myservice.domains = []
        self.assertEqual(myservice.domains, [])

        # origins
        self.assertEqual(myservice.origins, self.myorigins)
        myservice.origins = []
        self.assertEqual(myservice.origins, [])

        # flavor_id
        self.assertEqual(myservice.flavor_id, self.flavor_id)
        myservice.flavor_id = "standard"
        self.assertEqual(myservice.flavor_id, "standard")

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
            self.service_id,
            self.service_name, self.mydomains, self.myorigins, self.flavor_id,
            self.mycaching, self.myrestrictions)
        cloned_service = service.Service.init_from_dict(self.project_id,
                                                        myservice.to_dict())

        self.assertEqual(cloned_service.service_id, myservice.service_id)
        self.assertEqual(cloned_service.name, myservice.name)
        self.assertEqual(cloned_service.flavor_id, myservice.flavor_id)

        self.assertEqual([domain.to_dict() for domain
                          in cloned_service.domains],
                         [domain.to_dict() for domain
                          in myservice.domains])

        self.assertEqual([origin.to_dict() for origin
                          in cloned_service.origins],
                         [origin.to_dict() for origin
                          in myservice.origins])

        self.assertEqual([caching.to_dict()['rules'] for caching
                          in cloned_service.caching],
                         [caching.to_dict()['rules'] for caching
                          in myservice.caching])

        self.assertEqual([caching.to_dict()['name'] for caching
                          in cloned_service.caching],
                         [caching.to_dict()['name'] for caching
                          in myservice.caching])

        self.assertEqual([caching.to_dict()['ttl'] for caching
                          in cloned_service.caching],
                         [caching.to_dict()['ttl'] for caching
                          in myservice.caching])

        self.assertEqual([restrictions.to_dict()['rules'] for restrictions
                          in cloned_service.restrictions],
                         [restrictions.to_dict()['rules'] for restrictions
                          in myservice.restrictions])

        self.assertEqual([restrictions.to_dict()['name'] for restrictions
                          in cloned_service.restrictions],
                         [restrictions.to_dict()['name'] for restrictions
                          in myservice.restrictions])

    def test_init_from_dict_whitespaces(self):
        caching = [cachingrule.CachingRule('images ', 3600)]
        restrictions = [restriction.Restriction('client_ip ', 'whitelist')]
        name = 'tests '
        myservice = service.Service(
            self.service_id,
            name, self.mydomains, self.myorigins, self.flavor_id,
            caching, restrictions)
        cloned_service = service.Service.init_from_dict(self.project_id,
                                                        myservice.to_dict())
        self.assertNotEqual(cloned_service.name, myservice.name.strip())
        self.assertNotEqual([x.name for x in cloned_service.caching],
                            [y.name for y in myservice.caching])
        self.assertNotEqual([x.name for x in cloned_service.restrictions],
                            [y.name for y in myservice.restrictions])

    @ddt.data(u'', u'apple')
    def test_set_invalid_status(self, status):
        myservice = service.Service(
            self.service_id,
            self.service_name,
            self.mydomains,
            self.myorigins,
            self.flavor_id)

        self.assertRaises(ValueError, setattr, myservice, 'status', status)

    @ddt.data(u'create_in_progress', u'deployed', u'delete_in_progress')
    def test_set_valid_status(self, status):
        myservice = service.Service(
            self.service_id,
            self.service_name,
            self.mydomains,
            self.myorigins,
            self.flavor_id)

        myservice.status = status

        self.assertEqual(myservice.status, status)
