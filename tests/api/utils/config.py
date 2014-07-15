from cafe.engine.models.data_interfaces import ConfigSectionInterface


class cdnConfig(ConfigSectionInterface):
    """
    Defines the config values for cdn
    """
    SECTION_NAME = 'cdn'

    @property
    def base_url(self):
        """
        CDN endpoint
        """
        return self.get('base_url')


class authConfig(ConfigSectionInterface):
    """
    Defines the auth config values
    """
    SECTION_NAME = 'auth'

    @property
    def base_url(self):
        """
        Auth endpoint
        """
        return self.get('base_url')

    @property
    def user_name(self):
        """The name of the user, if applicable"""
        return self.get("user_name")

    @property
    def api_key(self):
        """The user's api key, if applicable"""
        return self.get_raw("api_key")

    @property
    def tenant_id(self):
        """The user's tenant_id, if applicable"""
        return self.get("tenant_id")
