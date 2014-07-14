from mock import patch
import unittest
import fastly

from oslo.config import cfg
from cdn.provider.fastly.driver import CDNProvider
from cdn.provider.fastly import controllers


class TestDriver(unittest.TestCase):

    def setUp(self):
        self.conf = cfg.CONF
        self.conf(project='cdn', prog='cdn', args=[])

    @patch('fastly.connect')
    def test_init(self, mock_connect):
        provider = CDNProvider(self.conf)
        mock_connect.assert_called_once_with(
            provider.conf['drivers:provider:fastly'].apikey)

    def test_is_alive(self):
        provider = CDNProvider(self.conf)
        self.assertEqual(provider.is_alive(), True)

    @patch.object(fastly, 'FastlyConnection')
    @patch('fastly.connect')
    def test_get_client(self, MockConnection, mock_connect):
        mock_connect.return_value = MockConnection(None, None)
        provider = CDNProvider(self.conf)
        client = provider.get_client()
        self.assertNotEquals(client, None)

    @patch('cdn.provider.fastly.controllers.ServiceController')
    def test_service_controller(self, MockController):
        provider = CDNProvider(self.conf)
        self.assertNotEquals(provider.service_controller, None)
