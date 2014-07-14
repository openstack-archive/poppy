import json

from cafe.engine.http import client
from models import requests


class AuthClient(client.HTTPClient):

    """
    Client Objects for Auth call
    """

    def __init__(self):
        super(AuthClient, self).__init__()

        self.default_headers['Content-Type'] = 'application/json'
        self.default_headers['Accept'] = 'application/json'

    def get_auth_token(self, url, user_name, api_key):
        """
        Get Auth Token using api_key
        @todo: Support getting token with password (or) api key.
        """
        request_body = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": user_name,
                    "apiKey": api_key
                },
            },
        }
        request_body = json.dumps(request_body)

        response = self.request('POST', url, data=request_body)
        token = response.json()['access']['token']['id']
        return token


class CDNClient(client.AutoMarshallingHTTPClient):

    """
    Client objects for all the CDN api calls
    """

    def __init__(self, url, auth_token, serialize_format="json",
                 deserialize_format="json"):
        super(CDNClient, self).__init__(serialize_format,
                                        deserialize_format)
        self.url = url
        self.auth_token = auth_token
        self.default_headers['X-Auth-Token'] = auth_token
        self.default_headers['Content-Type'] = 'application/json'
        self.default_headers['Accept'] = 'application/json'

        self.serialize = serialize_format
        self.deserialize_format = deserialize_format

    def create_service(self, service_name=None,
                       domain_list=None, origin_list=None,
                       caching_list=None, requestslib_kwargs=None):
        """
        Creates Service
        :return: Response Object containing response code 200 and body with
                details of service

        PUT
        services/{service_name}
        """
        url = '{0}/services/{1}'.format(self.url, service_name)
        request_object = requests.CreateService(domain_list=domain_list,
                                                origin_list=origin_list,
                                                caching_list=caching_list)
        return self.request('PUT', url,
                            request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_service(self, service_name):
        """Get Service
        :return: Response Object containing response code 200 and body with
        details of service
        """

        url = '{0}/services/{1}'.format(self.url, service_name)
        return self.request('GET', url)

    def delete_service(self, service_name):
        """Delete Service
        :return: Response Object containing response code 204
        """

        url = '{0}/services/{1}'.format(self.url, service_name)
        return self.request('DELETE', url)
