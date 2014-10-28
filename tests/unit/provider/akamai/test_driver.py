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

import akamai
import mock
from oslo.config import cfg

from poppy.common import util
from poppy.provider.akamai import driver
from tests.unit import base

AKAMAI_OPTIONS = [
    cfg.StrOpt('client_token', default='ccc',
               help='Akamai client token'),
    cfg.StrOpt('client_secret', default='sss',
               help='Akamai client secret'),
    cfg.StrOpt('access_token', default='aaa',
               help='Akamai access token'),
    cfg.StrOpt('base_url', default='/abc',
               help='Akamai partner API base URL'),
    cfg.StrOpt('base_ccu_url', default='/abc',
               help='Akamai CCU Purge API base URL'),
    cfg.StrOpt('domain_link_suffix', default='.v2.mdc.edgesuite.net',
               help='Akamai domain link suffix returned by '),
]


class TestDriver(base.TestCase):

    def setUp(self):
        super(TestDriver, self).setUp()

        self.conf = cfg.ConfigOpts()

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_init(self, mock_connect):
        provider = driver.CDNProvider(self.conf)
        mock_connect.assert_called_once_with(
            client_token=(
                provider._conf['drivers:provider:akamai'].client_token),
            client_secret=(
                provider._conf['drivers:provider:akamai'].client_secret),
            access_token=(
                provider._conf['drivers:provider:akamai'].access_token)
        )
        self.assertEqual('Akamai', provider.provider_name)

    def test_is_alive(self):
        provider = driver.CDNProvider(self.conf)
        self.assertEqual(True, provider.is_alive())

    @mock.patch('akamai.edgegrid.EdgeGridAuth')
    @mock.patch.object(driver, 'AKAMAI_OPTIONS', new=AKAMAI_OPTIONS)
    def test_get_client(self, mock_connect):
        mock_connect.return_value = mock.Mock()
        provider = driver.CDNProvider(self.conf)
        self.assertNotEqual(None, provider.client)
