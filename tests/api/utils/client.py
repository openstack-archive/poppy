# coding= utf-8

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
import time

from cafe.engine.http import client

from tests.api.utils.models import requests


class AuthClient(client.HTTPClient):

    """Client Objects for Auth call."""

    def __init__(self):
        super(AuthClient, self).__init__()

        self.default_headers['Content-Type'] = 'application/json'
        self.default_headers['Accept'] = 'application/json'

    def authenticate_user(self, auth_url, user_name, api_key):
        """Get Auth Token & Project ID using api_key

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
        project_id = response.json()['access']['token']['tenant']['id']
        return token, project_id


class PoppyClient(client.AutoMarshallingHTTPClient):

    """Client objects for all the Poppy api calls."""

    def __init__(self, url, auth_token, project_id, serialize_format="json",
                 deserialize_format="json"):
        super(PoppyClient, self).__init__(serialize_format,
                                          deserialize_format)
        self.url = url
        self.auth_token = auth_token
        self.project_id = project_id
        self.default_headers['X-Auth-Token'] = auth_token
        self.default_headers['X-Project-Id'] = project_id
        self.default_headers['Content-Type'] = 'application/json'

        self.serialize = serialize_format
        self.deserialize_format = deserialize_format

    def create_service(self, service_name=None,
                       domain_list=None, origin_list=None,
                       caching_list=None, restrictions_list=None,
                       requestslib_kwargs=None,
                       flavor_id=None,
                       log_delivery=None):
        """Creates Service

        :return: Response Object containing response code 200 and body with
                details of service
        PUT
        services/{service_name}
        """
        url = '{0}/services'.format(self.url)

        if not log_delivery:
            log_delivery = {"enabled": False}

        if log_delivery:
            request_object = requests.CreateService(
                service_name=service_name,
                domain_list=domain_list,
                origin_list=origin_list,
                caching_list=caching_list,
                restrictions_list=restrictions_list,
                flavor_id=flavor_id,
                log_delivery=log_delivery)
        else:
            request_object = requests.CreateService(
                service_name=service_name,
                domain_list=domain_list,
                origin_list=origin_list,
                caching_list=caching_list,
                restrictions_list=restrictions_list,
                flavor_id=flavor_id)

        return self.request('POST', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def patch_service(self, location, request_body=None,
                      requestslib_kwargs=None):
        """Updates Service

        :return: Response code 202 with location header
        PATCH
        services/{service_name}
        """
        request_object = requests.PatchService(request_body=request_body)
        return self.request('PATCH', location, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_service(self, location=None):
        """Get Service

        :return: Response Object containing response code 200 and body with
        details of service
        GET
        services/{service_id}
        """
        return self.request('GET', location)

    def list_services(self, param=None):
        """Get a list of Services

        :return: Response Object containing response code 200 and body with
        list of services & details
        GET
        services
        """

        url = '{0}/services'.format(self.url)
        return self.request('GET', url, params=param)

    def delete_service(self, location):
        """Delete Service

        :return: Response Object containing response code 204
        DELETE
        services/{service_id}
        """

        return self.request('DELETE', location)

    def admin_service_action(self, project_id, action,
                             requestslib_kwargs=None):
        """Update Tenant State

        :return: Response Object containing response code 202
        POST
        /admin/services/action
        """

        url = '{0}/admin/services/action'.format(self.url)
        request_object = requests.ServiceAction(
            project_id=project_id, action=action)
        return self.request('POST', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def admin_migrate_domain(self, project_id, service_id, domain, new_cert,
                             requestslib_kwargs=None):
        """Update SAN domain

        :return: Response Object containing response code 202
        POST
        /admin/provider/akamai/service
        """

        url = '{0}/admin/provider/akamai/service'.format(self.url)
        request_object = requests.MigrateSANDomain(
            project_id=project_id, service_id=service_id, domain=domain,
            new_cert=new_cert)
        return self.request('POST', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def check_health(self):
        """Check Health of the application

        :return: Response Object containing response code 204
        GET
        health
        """

        url = '{0}/health'.format(self.url)
        return self.request('GET', url)

    def ping(self):
        """Ping the server

        :return: Response Object containing response code 204
        GET
        ping
        """

        url = '{0}/ping'.format(self.url)
        return self.request('GET', url, headers={'Accept': "application/json"})

    def create_flavor(self, flavor_id=None, provider_list=None, limits=None,
                      requestslib_kwargs=None):
        """Create flavor

        :return: Response Object containing response code 204 and header with
                 Location
        PUT
        flavors/{flavor_id}
        """
        url = '{0}/flavors'.format(self.url)
        request_object = requests.CreateFlavor(
            flavor_id=flavor_id,
            provider_list=provider_list,
            limits=limits)
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
            url = flavor_location
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
            url = flavor_location
        else:
            url = u'{0}/flavors/{1}'.format(self.url, flavor_id)

        return self.request('DELETE', url)

    def purge_asset(self, location=None, asset_url='all=True'):
        """Delete Asset

        :return: Response Object containing response code 204
        DELETE
        services/{service_id}/assets​{?url,​all}
        """
        if asset_url != 'all=True':
            asset_url = 'url=' + asset_url

        url = '{0}/services/assets?{1}'.format(location, asset_url)
        return self.request('DELETE', url)

    def wait_for_service_status(self, location, status,
                                abort_on_status=None,
                                retry_interval=2,
                                retry_timeout=30):
        """Waits for a service to reach a given status."""
        current_status = ''
        start_time = int(time.time())
        stop_time = start_time + retry_timeout
        while current_status.lower() != status.lower():
            time.sleep(retry_interval)
            service = self.get_service(location=location)
            body = service.json()
            current_status = body['status']
            if (current_status.lower() == status.lower()):
                return service

            if abort_on_status is not None:
                if current_status == abort_on_status:
                    # this is for debugging purpose,
                    # will be removed later, so simply use print
                    print(body.get('errors', []))
                    return service

            current_time = int(time.time())
            if current_time > stop_time:
                assert False, ('Timed out waiting for service status change'
                               ' to {0}').format(status)

    def wait_for_service_delete(self, location,
                                abort_on_status=None,
                                retry_interval=2,
                                retry_timeout=30):
        """Waits for a service to be deleted."""
        current_status = ''
        start_time = int(time.time())
        stop_time = start_time + retry_timeout
        resp = self.get_service(location=location)
        while resp.status_code == 200:
            time.sleep(retry_interval)
            resp = self.get_service(location=location)
            if (resp.status_code == 404):
                return resp

            if abort_on_status is not None:
                if current_status == abort_on_status:
                    # this is for debugging purpose,
                    # will be removed later, so simply use print
                    print(resp.get('errors', []))
                    return resp

            current_time = int(time.time())
            if current_time > stop_time:
                assert False, ('Timed out waiting for service to be deleted')
