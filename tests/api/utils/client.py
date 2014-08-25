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

from cafe.engine.http import client

from tests.api.utils.models import requests as requests_model


class AuthClient(client.HTTPClient):

    """Client Objects for Auth call."""

    def __init__(self):
        super(AuthClient, self).__init__()

        self.default_headers['Content-Type'] = 'application/json'
        self.default_headers['Accept'] = 'application/json'

    def get_auth_token(self, auth_url, user_name, api_key):
        """Get Auth Token using api_key

        TODO (malini-kamalambal): Support getting token with password (or)
                                  api key.
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
        url = auth_url + '/tokens'

        response = self.request('POST', url, data=request_body)
        token = response.json()['access']['token']['id']
        return token


class PoppyClient(client.AutoMarshallingHTTPClient):

    """Client objects for all the Poppy api calls."""

    def __init__(self, url, auth_token, serialize_format="json",
                 deserialize_format="json"):
        super(PoppyClient, self).__init__(serialize_format,
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
        """Creates Service

        :return: Response Object containing response code 200 and body with
                details of service
        PUT
        services/{service_name}
        """
        url = '{0}/services/{1}'.format(self.url, service_name)
        request_object = requests_model.CreateService(
            domain_list=domain_list,
            origin_list=origin_list,
            caching_list=caching_list)
        return self.request('PUT', url,
                            request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_service(self, service_name):
        """Get Service

        :return: Response Object containing response code 200 and body with
        details of service
        GET
        services/{service_name}
        """

        url = '{0}/services/{1}'.format(self.url, service_name)
        return self.request('GET', url)

    def delete_service(self, service_name):
        """Delete Service

        :return: Response Object containing response code 204
        DELETE
        services/{service_name}
        """

        url = '{0}/services/{1}'.format(self.url, service_name)
        return self.request('DELETE', url)

    def create_flavor(self, flavor_id=None, provider_list=None,
                      requestslib_kwargs=None):
        """Create flavor

        :return: Response Object containing response code 204 and header with
                 Location
        PUT
        flavors/{flavor_id}
        """
        url = '{0}/flavors/{1}'.format(self.url, flavor_id)
        request_object = requests_model.CreateFlavor(
            flavor_id=flavor_id,
            provider_list=provider_list)
        return self.request('POST', url,
                            request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_flavor(self, flavor_location=None, flavor_id=None):
        """Get Flavor

        :return: Response Object containing response code 200 and body with
        details of flavor
        GET
        flavors/{flavor_id}
        """
        if flavor_location:
            url = '{0}{1}'.format(self.url, flavor_location)
        else:
            url = '{0}/flavors/{1}'.format(self.url, flavor_id)

        return self.request('GET', url)

    def delete_flavor(self, flavor_location=None, flavor_id=None):
        """Delete Flavor

        :return: Response Object containing response code 204
        DELETE
        flavors/{flavor_id}
        """
        if flavor_location:
            url = '{0}{1}'.format(self.url, flavor_location)
        else:
            url = '{0}/flavors/{1}'.format(self.url, flavor_id)

        return self.request('DELETE', url)
