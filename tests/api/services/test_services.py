import ddt
import uuid

from tests.api.utils import base
from tests.api.utils.schema import response


@ddt.ddt
class TestServices(base.TestBase):

    """Tests for Services."""

    def setUp(self):
        super(TestServices, self).setUp()
        self.service_name = uuid.uuid1()

    @ddt.file_data('create_service.json')
    def test_create_service(self, test_data):

        domain_list = test_data['domain_list']
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list)
        self.assertEqual(resp.status_code, 201)

        response_body = resp.json()
        self.assertSchema(response_body, response.create_service)

        #Get on Created Service
        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(body['domains'], domain_list)
        self.assertEqual(body['origins'], origin_list)
        self.assertEqual(body['caching_list'], caching_list)

    test_create_service.tags = ['smoke', 'positive']

    def tearDown(self):
        super(TestServices, self).tearDown()
