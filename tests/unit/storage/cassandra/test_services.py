from cdn.storage.cassandra.services import ServicesController
from mock import patch, Mock
import cassandra

from unittest import TestCase


class CassandraStorageTests(TestCase):

    @patch.object(ServicesController, 'session')
    @patch.object(cassandra.cluster.Session, 'execute')
    def test_get_service(self, mock_session, mock_execute):
        project_id = 123456
        service_name = 'mock_service'

        sc = ServicesController(None)
        sc.get(project_id, service_name)

        mock_execute.execute.assert_called_with(args={project_id})

        pass
