import cassandra
import json
from cdn.storage.cassandra.services import ServicesController
from mock import patch
from unittest import TestCase


class CassandraStorageTests(TestCase):

    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service(self, mock_session, mock_execute):
        project_id = 123456
        service_name = 'mock_service'

        cassandra_response = []
        cassandra_response.append(project_id)
        cassandra_response.append(service_name)

        domains = ["{domain: 'www.mocksite.com'}"]
        origins = ["{origin: 'www.mocksite.com'}"]
        caching_rules = ["{name: 'www.mocksite.com'}"]
        restrictions = ["{rules: 'www.mocksite.com'}"]

        cassandra_response.append(domains)
        cassandra_response.append(origins)
        cassandra_response.append(caching_rules)
        cassandra_response.append(restrictions)

        # mock the response from cassandra
        mock_execute.execute.return_value = json.dumps([cassandra_response])

        sc = ServicesController(None)
        actual_response = json.loads(sc.get(project_id, service_name))

        self.assertEqual(actual_response[0][0], project_id)
        self.assertEqual(actual_response[0][1], service_name)
