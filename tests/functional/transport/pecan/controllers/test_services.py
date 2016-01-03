# -*- coding: utf8 -*-
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

import json
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
import uuid

import ddt
from oslo_config import cfg
import pecan

from poppy.dns.default.services import ServicesController
from poppy.transport.pecan.controllers import base as c_base
from tests.functional.transport.pecan import base

LIMITS_OPTIONS = [
    cfg.IntOpt('max_services_per_page', default=20,
               help='Max number of services per page for list services'),
]

LIMITS_GROUP = 'drivers:transport:limits'

_MAX_SERVICE_OPTIONS = [
    cfg.IntOpt('max_services_per_project', default=20,
               help='Default max service per project_id')
]

_MAX_SERVICE_GROUP = 'drivers:storage'


@ddt.ddt
class ServiceControllerTest(base.FunctionalTest):

    def setUp(self):
        super(ServiceControllerTest, self).setUp()
        self.conf.register_opts(_MAX_SERVICE_OPTIONS, group=_MAX_SERVICE_GROUP)
        self.max_services_per_project = \
            self.conf[_MAX_SERVICE_GROUP].max_services_per_project
        self.project_id = str(uuid.uuid1())
        self.service_name = str(uuid.uuid1())
        self.flavor_id = str(uuid.uuid1())

        # create a mock flavor to be used by new service creations
        flavor_json = {
            "id": self.flavor_id,
            "providers": [
                {
                    "provider": "mock",
                    "links": [
                        {
                            "href": "http://mock.cdn",
                            "rel": "provider_url"
                        }
                    ]
                }
            ]
        }
        response = self.app.post('/v1.0/flavors',
                                 params=json.dumps(flavor_json),
                                 headers={
                                     "Content-Type": "application/json",
                                     "X-Project-ID": self.project_id})

        self.assertEqual(201, response.status_code)

        # create an initial service to be used by the tests
        self.service_json = {
            "name": self.service_name,
            "domains": [
                {"domain": "test.mocksite.com"},
                {"domain": "blog.mocksite.com"}
            ],
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 80,
                    "ssl": False
                }
            ],
            "flavor_id": self.flavor_id,
            "caching": [
                {
                    "name": "default",
                    "ttl": 3600
                }
            ],
            "restrictions": [
                {
                    "name": "website only",
                    "type": "whitelist",
                    "rules": [
                        {
                            "name": "mocksite.com",
                            "referrer": "www.mocksite.com"
                        }
                    ]
                }
            ]
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(self.service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)
        self.assertTrue('Location' in response.headers)

        self.service_url = urlparse.urlparse(response.headers["Location"]).path

    def tearDown(self):
        super(ServiceControllerTest, self).tearDown()

        # delete the mock flavor
        # response = self.app.delete('/v1.0/flavors/' + self.flavor_id)
        # self.assertEqual(204, response.status_code)

        # delete the test service
        # response = self.app.delete('/v1.0/services/' + self.service_name)
        # self.assertEqual(200, response.status_code)

    def test_get_all(self):
        response = self.app.get('/v1.0/services',
                                headers={'X-Project-ID': self.project_id})

        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.body.decode("utf-8"))
        self.assertTrue("links" in response_dict)
        self.assertTrue("services" in response_dict)

    def test_get_more_than_max_services_per_page(self):
        self.conf.register_opts(LIMITS_OPTIONS, group=LIMITS_GROUP)
        self.limits_conf = self.conf[LIMITS_GROUP]
        self.max_services_per_page = self.limits_conf.max_services_per_page

        response = self.app.get('/v1.0/services',
                                headers={'X-Project-ID': self.project_id},
                                params={
                                    "marker": uuid.uuid4(),
                                    "limit": self.max_services_per_page + 1
                                },
                                expect_errors=True)

        self.assertEqual(400, response.status_code)

    def test_get_one(self):
        response = self.app.get(
            self.service_url,
            headers={'X-Project-ID': self.project_id})

        self.assertEqual(200, response.status_code)

        response_dict = json.loads(response.body.decode("utf-8"))
        self.assertTrue("domains" in response_dict)
        self.assertTrue("origins" in response_dict)

    def test_get_one_not_exist(self):
        response = self.app.get('/v1.0/services/' + str(uuid.uuid4()),
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-Project-ID': self.project_id},
                                expect_errors=True)

        self.assertEqual(404, response.status_code)

    @ddt.file_data("data_create_service.json")
    def test_create(self, service_json):

        # override the hardcoded flavor_id in the ddt file with
        # a custom one defined in setUp()
        service_json['flavor_id'] = self.flavor_id

        # create with good data
        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id})
        self.assertEqual(202, response.status_code)

    @ddt.file_data("data_create_service.json")
    def test_create_hit_service_limits(self, service_json):

        # override the hardcoded flavor_id in the ddt file with
        # a custom one defined in setUp()
        service_json['flavor_id'] = self.flavor_id
        project_id = str(uuid.uuid4())
        service_urls = []
        for _ in range(self.max_services_per_project):
            # create with good data
            response = self.app.post('/v1.0/services',
                                     params=json.dumps(service_json),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'X-Project-ID': project_id})
            service_urls.append(response.headers['Location'])
            self.assertEqual(202, response.status_code)

        # Now create another service, and receive a 403

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': project_id},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)

    def test_patch_shared_ssl_domain(self):

        service_json = {
            "name": "mocksite.com",
            "domains": [
                {"domain": "mocksite",
                 'protocol': 'https',
                 'certificate': 'shared'}
            ],
            "flavor_id": self.flavor_id,
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 443,
                    "ssl": True
                }
            ]
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 })
        self.assertEqual(202, response.status_code)

        # NOTE (TheSriram): One shard is already taken, since we have a
        # service created with it. Create n-1 services with n being
        # total number of shared shards

        class MockDriver(object):
            def __init__(self):
                super(MockDriver, self).__init__()

            def dns_name(self):
                return 'mock_dns'

        total_shards = ServicesController(
            driver=MockDriver()).shared_ssl_shards

        for shard_id in range(total_shards - 1):
            service_json = {
                "name": "mocksite.com",
                "domains": [
                    {"domain": "mocksiteshard{0}".format(shard_id),
                     'protocol': 'https',
                     'certificate': 'shared'}
                ],
                "flavor_id": self.flavor_id,
                "origins": [
                    {
                        "origin": "mocksite.com",
                        "port": 443,
                        "ssl": True
                    }
                ]
            }

            response = self.app.post('/v1.0/services',
                                     params=json.dumps(service_json),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'X-Project-ID': self.project_id
                                     })
            self.assertEqual(202, response.status_code)
            response = self.app.patch(response.location,
                                      params=json.dumps([{
                                          "op": "add",
                                          "path": "/domains/-",
                                          "value": {
                                                "domain": "mocksite",
                                                "protocol": "https",
                                                "certificate": "shared"}
                                      }]),
                                      headers={'Content-Type':
                                               'application/json',
                                               'X-Project-ID':
                                               self.project_id
                                               }, expect_errors=True)
            self.assertEqual(202, response.status_code)

        # NOTE(TheSriram): Now create another service, and patch it.
        # with all shards Exhausted, this will result in a 400

        service_json = {
            "name": "mocksite.com",
            "domains": [
                {"domain": "mocksitefinal",
                 'protocol': 'https',
                 'certificate': 'shared'}
            ],
            "flavor_id": self.flavor_id,
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 443,
                    "ssl": True
                }
            ]
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 })
        self.assertEqual(202, response.status_code)
        response = self.app.patch(response.location,
                                  params=json.dumps([{
                                      "op": "add",
                                      "path": "/domains/-",
                                      "value": {
                                            "domain": "mocksite",
                                            "protocol": "https",
                                            "certificate": "shared"}
                                  }]),
                                  headers={'Content-Type': 'application/json',
                                           'X-Project-ID': self.project_id
                                           }, expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertTrue('has already been taken' in response)

    def test_patch_blacklist_on_whitelist(self):
        service_json = {
            "name": "mocksite.com",
            "domains": [
                {"domain": "blog.mocksite.com"}
            ],
            "flavor_id": self.flavor_id,
            "origins": [
                {
                    "origin": "mocksite.com",
                    "port": 443,
                    "ssl": True
                }
            ],
            "restrictions": [
                {
                    "name": "website only",
                    "access": "whitelist",
                    "rules": [
                        {
                            "name": "mocksite.com",
                            "geography": "USA"
                        }
                    ]
                }
            ]
        }

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 })
        self.assertEqual(202, response.status_code)

        response = self.app.patch(response.location,
                                  params=json.dumps([{
                                      "op": "add",
                                      "path": "/restrictions/-",
                                      "value": {
                                            "name": "Restriction 6",
                                            "access": "blacklist",
                                            "rules": [{
                                                "name": "rule2",
                                                "geography": "North America"
                                            }]
                                      }
                                  }]),
                                  headers={'Content-Type': 'application/json',
                                           'X-Project-ID': self.project_id
                                           }, expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertTrue('Cannot blacklist and whitelist' in response)

    def test_create_with_invalid_json(self):
        # create with errorenous data: invalid json data
        response = self.app.post('/v1.0/services',
                                 params="{",
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_create_service_bad_input_json.json")
    def test_create_with_bad_input_json(self, service_json):
        # create with errorenous data
        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    @ddt.file_data("data_create_service_duplicate.json")
    def test_create_with_duplicate_name(self, service_json):
        # override name
        service_json['name'] = self.service_name
        service_json['flavor_id'] = self.flavor_id

        response = self.app.post('/v1.0/services',
                                 params=json.dumps(service_json),
                                 headers={
                                     'Content-Type': 'application/json',
                                     'X-Project-ID': self.project_id
                                 },
                                 expect_errors=True)
        self.assertEqual(202, response.status_code)

    def test_update_with_bad_input(self):
        # update with erroneous data
        response = self.app.patch(self.service_url,
                                  params=json.dumps({
                                      "origins": [
                                          {
                                              # missing "origin" here
                                              "port": 80,
                                              "ssl": False
                                          }
                                      ]
                                  }),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'X-Project-ID': self.project_id
                                  },
                                  expect_errors=True)

        self.assertEqual(400, response.status_code)

    def test_update_with_good_input(self):
        self.skipTest('Skip failing test')
        response = self.app.get(
            self.service_url,
            headers={'X-Project-ID': self.project_id})
        self.assertEqual(200, response.status_code)
        # update with good data
        response = self.app.patch(self.service_url,
                                  params=json.dumps([
                                      {
                                          "op": "replace",
                                          "path": "/origins/0",
                                          "value": {
                                              "origin": "44.33.22.11",
                                              "port": 80,
                                              "ssl": "false"
                                          }
                                      }
                                  ]),
                                  headers={
                                      'Content-Type': 'application/json',
                                      'X-Project-ID': self.project_id
                                  })
        self.assertEqual(202, response.status_code)

    def test_patch_non_exist(self):
        # This is for coverage 100%
        response = self.app.patch(
            "/v1.0/services/{0}".format(str(uuid.uuid4())),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            params=json.dumps([
                {
                    "op": "add",
                    "path": "/origins/0",
                    "value": {
                        "origin": "44.33.22.11",
                        "port": 80,
                        "ssl": "false"
                    }
                }
            ]),
            expect_errors=True)
        self.assertEqual(404, response.status_code)

        class FakeController(c_base.Controller):

            @pecan.expose("json")
            def patch_all(self):
                return "Hello World!"

        self.test_fake_controller = FakeController(None)
        patch_ret_val = self.test_fake_controller._handle_patch('patch', '')
        self.assertTrue(len(patch_ret_val) == 2)

    def test_delete(self):
        response = self.app.delete(
            self.service_url,
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            }
        )
        self.assertEqual(202, response.status_code)

        # TODO(amitgandhinz): commented out as thread model
        # is not allowing thread to process with test

        # check if it actually gets deleted
        # status_code = 0
        # count = 0
        # while (count < 5):
        #     service_deleted = self.app.get(
        #         '/v1.0/services/' + self.service_name,
        #         headers={'X-Project-ID': self.project_id},
        #         expect_errors=True)

        #     status_code = service_deleted.status_code
        #     print("service delete status: %s" % status_code)

        #     if status_code == 200:
        #         print 'not yet deleted, so try again in 1s'
        #         import time
        #         time.sleep(1)
        #     else:
        #         break

        #     count = count + 1

        # self.assertEqual(404, status_code)

    def test_delete_non_exist(self):
        response = self.app.delete(
            "/v1.0/services/{0}".format(str(uuid.uuid4())),
            headers={
                'Content-Type': 'application/json',
                'X-Project-ID': self.project_id
            },
            expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_purge_non_exist(self):
        # This is for coverage 100%
        response = self.app.delete(
            "/v1.0/services/{0}/assets?all=true".format(str(uuid.uuid4())),
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)
        self.assertEqual(404, response.status_code)

    def test_purge_error_parms(self):
        response = self.app.delete(
            self.service_url + '/assets',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)

        response = self.app.delete(
            self.service_url + '/assets?all=true&url=/abc',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(400, response.status_code)

    def test_purge_all(self):
        response = self.app.delete(
            self.service_url + '/assets?all=True',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)

    def test_purge_url_and_all(self):
        response = self.app.delete(
            self.service_url + '/assets?all=True',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)

    def test_purge_single_url(self):
        response = self.app.delete(
            self.service_url + '/assets?url=/abc',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)

    def test_purge_single_url_non_ascii(self):
        response = self.app.delete(
            self.service_url + '/assets?url=/¢/*',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(400, response.status_code)

    @ddt.data('True', 'true', 'tRuE')
    def test_purge_single_url_and_hard_invalidate(self, hard):
        response = self.app.delete(
            self.service_url + '/assets?url=/abc&hard={0}'.format(hard),
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)

    @ddt.data('False', 'false', 'fALsE')
    def test_purge_single_url_and_soft_invalidate(self, hard):
        response = self.app.delete(
            self.service_url + '/assets?url=/abc&hard={0}'.format(hard),
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)

    def test_purge_no_url_with_querystring(self):
        response = self.app.delete(
            self.service_url + '/assets?hard=True',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)

    def test_purge_no_url(self):
        response = self.app.delete(
            self.service_url + '/assets',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)

    def test_purge_wildcard_url_and_soft_invalidate(self):
        response = self.app.delete(
            self.service_url + '/assets?url=/abc/*&hard=False',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)

    def test_purge_single_url_and_non_boolean_invalidate(self):
        response = self.app.delete(
            self.service_url + '/assets?url=/abc&hard=Idonteven',
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(400, response.status_code)

    @ddt.data(True, False)
    def test_purge_none_url(self, hard):
        response = self.app.delete(
            self.service_url + '/assets?url=None&hard={0}'.format(hard),
            headers={
                "Content-Type": "application/json",
                'X-Project-ID': self.project_id
            },
            expect_errors=True)

        self.assertEqual(202, response.status_code)
        self.assertEqual(self.service_url,
                         urlparse.urlparse(response.headers["Location"]).path)
