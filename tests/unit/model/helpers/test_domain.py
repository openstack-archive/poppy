# -*- coding: utf-8 -*-
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
from tests.unit import base


@ddt.ddt
class TestDomain(base.TestCase):

    @ddt.unpack
    @ddt.data({'domain_name': 'www.mydomain.com',
               'changed_domain_name': 'www.changed-domain.com'},
              {'domain_name': u'www.düsseldorf-Lörick.com',
               'changed_domain_name': u'www.düsseldorf.com'
               },
              {'domain_name': u'WWW.UPPERCASE.COM',
               'changed_domain_name': u'WWW.UPPERCASE-CHANGED.COM'
               })
    def test_domain(self, domain_name, changed_domain_name):
        mydomain = domain.Domain(domain_name)
        self.assertTrue(mydomain.domain.islower())

        # test all properties
        # domain
        self.assertEqual(mydomain.domain, domain_name.lower())
        self.assertEqual(mydomain.protocol, 'http')
        self.assertEqual(mydomain.certificate, None)
        mydomain.domain = changed_domain_name
        self.assertEqual(mydomain.domain, changed_domain_name.lower())
        try:
            mydomain.certificate = 'SAN'
        except ValueError:
            self.assertTrue(True)

        my_other_domain = domain.Domain.init_from_dict({"domain": domain_name})
        self.assertEqual(my_other_domain.domain, domain_name.lower())

        try:
            domain.Domain(domain_name, 'https')
        except ValueError:
            self.assertTrue(True)

        my_https_domain = domain.Domain(domain_name, 'https', 'san')
        self.assertEqual(my_https_domain.protocol, 'https')
        self.assertEqual(my_https_domain.certificate, 'san')

        try:
            my_https_domain.certificate = 'non-sense'
        except ValueError:
            self.assertTrue(True)
