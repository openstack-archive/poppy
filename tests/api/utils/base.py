import jsonschema

from cafe.drivers.unittest import fixtures

from tests.api.utils import client
from tests.api.utils import config


class TestBase(fixtures.BaseTestFixture):
    """Child class of fixtures.BaseTestFixture for testing CDN.

    Inherit from this and write your test methods. If the child class defines
    a prepare(self) method, this method will be called before executing each
    test method.
    """

    @classmethod
    def setUpClass(cls):

        super(TestBase, cls).setUpClass()

        cls.auth_config = config.authConfig()
        cls.auth_client = client.AuthClient()
        auth_token = cls.auth_client.get_auth_token(cls.auth_config.base_url,
                                                    cls.auth_config.user_name,
                                                    cls.auth_config.api_key)

        cls.config = config.cdnConfig()
        cls.url = cls.config.base_url

        cls.client = client.CDNClient(cls.url, auth_token,
                                      serialize_format='json',
                                      deserialize_format='json')

    def assertSchema(self, response_json, expected_schema):
        """Verify response schema aligns with the expected schema
        """
        try:
            jsonschema.validate(response_json, expected_schema)
        except jsonschema.ValidationError as message:
            assert False, message

    @classmethod
    def tearDownClass(cls):
        """
        Deletes the added resources
        """
        super(TestBase, cls).tearDownClass()
