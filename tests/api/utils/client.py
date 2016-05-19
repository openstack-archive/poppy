# coding= utf-8

# Copyright (c) 2015 Rackspace, Inc.
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
import pyrax
import requests as python_requests
import time

from cafe.engine.http import client

from tests.api.utils.models import requests


class AuthClient(client.HTTPClient):

    """Client Objects for Auth call."""

    def __init__(self):
        super(AuthClient, self).__init__()

        self.default_headers['Content-Type'] = 'application/json'
        self.default_headers['Accept'] = 'application/json'

    def authenticate_user(self, auth_url, user_name, api_key=None,
                          password=None):
        """Get Auth Token & Project ID using api_key"""

        if api_key:
            request_body = {
                "auth": {
                    "RAX-KSKEY:apiKeyCredentials": {
                        "username": user_name,
                        "apiKey": api_key
                    },
                },
            }
        elif password:
            request_body = {
                "auth": {
                    "passwordCredentials": {
                        "username": user_name,
                        "password": password
                    },
                },
            }

        request_body = json.dumps(request_body)
        url = auth_url + '/tokens'

        response = self.request('POST', url, data=request_body)
        token = response.json()['access']['token']['id']
        project_id = response.json()['access']['token']['tenant']['id']
        return token, project_id


class DNSClient(client.HTTPClient):

    def __init__(self, username, api_key):
        super(DNSClient, self).__init__()

        self.username = username
        self.api_key = api_key

        pyrax.set_setting('identity_type', 'rackspace')
        pyrax.set_credentials(self.username,
                              self.api_key)

    def verify_domain_migration(self, access_url, suffix):
        # Note: use rindex to find last occurrence of the suffix
        shard_name = access_url[:access_url.rindex(suffix) - 1].split('.')[-1]
        subdomain_name = '.'.join([shard_name, suffix])

        # get subdomain
        subdomain = pyrax.cloud_dns.find(name=subdomain_name)
        # search and find the CNAME record
        name = access_url
        record_type = 'CNAME'
        records = pyrax.cloud_dns.search_records(subdomain, record_type, name)
        return records[0].data


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

    def get_service(self, location=None,
                    requestslib_kwargs=None):
        """Get Service

        :return: Response Object containing response code 200 and body with
        details of service
        GET
        services/{service_id}
        """
        return self.request('GET', location,
                            requestslib_kwargs=requestslib_kwargs)

    def purge_assets(self, location, param=None, requestslib_kwargs=None):
        """Purge Assets

        :return: Response Object containing response code 204
        DELETE
        /services/{service_id}/assets​?{url,​all}
        """
        url = '{0}/assets'.format(location)

        return self.request('DELETE', url, params=param,
                            requestslib_kwargs=requestslib_kwargs)

    def list_services(self, param=None,
                      requestslib_kwargs=None):
        """Get a list of Services

        :return: Response Object containing response code 200 and body with
        list of services & details
        GET
        services
        """

        url = '{0}/services'.format(self.url)
        return self.request('GET', url, params=param,
                            requestslib_kwargs=requestslib_kwargs)

    def delete_service(self, location, requestslib_kwargs=None):
        """Delete Service

        :return: Response Object containing response code 204
        DELETE
        services/{service_id}
        """

        return self.request('DELETE', location,
                            requestslib_kwargs=requestslib_kwargs)

    def get_analytics(self, location, domain, start_time, metric_type,
                      end_time=None, requestslib_kwargs=None):
        """Get Analytics for the domain

        :return: Response Object containing response code 200
        GET
        location/analytics?domain=domain&startTime=startTime&endTime=endTime
        &metricType=metricType
        """
        if end_time:
            url = location + \
                u'/analytics?domain={0}&startTime={1}&endTime={2}&metricType={3}'.format(  # noqa
                    domain, start_time, end_time, metric_type)
        else:
            url = location + \
                u'/analytics?domain={0}&startTime={1}&metricType={2}'.format(
                    domain, start_time, metric_type)

        # CAFE requests bombs with hypothesis test data
        return python_requests.get(url, headers=self.default_headers)
        # return self.request(
        #    'GET', url, requestslib_kwargs=requestslib_kwargs)

    def admin_get_service_by_domain_name(self, domain):
        """Get Service By domain name

        :return: Response Object containing response code 200 and body with
        details of service
        GET
        domain/{domain_name}
        """

        domain_url = '{0}/admin/domains/{1}'.format(self.url, domain)
        return self.request('GET', domain_url)

    def admin_service_action(self, action, project_id=None, domain=None,
                             requestslib_kwargs=None):
        """Update Tenant State

        :return: Response Object containing response code 202
        POST
        /admin/services/action
        """

        url = '{0}/admin/services/action'.format(self.url)
        request_object = requests.ServiceAction(
            project_id=project_id, action=action, domain=domain)
        return self.request('POST', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def admin_service_limit(self, project_id, limit=None,
                            requestslib_kwargs=None):
        """Update Tenant State Limit

        :return: Response Object containing response code 201
        POST
        /admin/limits
        """

        url = '{0}/admin/limits/{1}'.format(self.url, project_id)
        request_object = requests.ServiceLimit(limit=limit)
        return self.request('PUT', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_admin_service_limit(self, project_id,
                                requestslib_kwargs=None):
        """Get Tenant State Limit

        :return: Response Object containing response code 200
        GET
        /admin/limits/{project_id}
        """

        url = '{0}/admin/limits/{1}'.format(self.url, project_id)
        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

    def set_service_status(self, project_id, service_id, status,
                           requestslib_kwargs=None):
        """Set Service State

        :return: Response Object containing response code 201

        POST
        /admin/services/status
        """

        url = '{0}/admin/services/status'.format(self.url)
        request_object = requests.ServiceStatus(
            status=status,
            project_id=project_id,
            service_id=service_id
        )
        return self.request('POST', url, request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_by_service_status(self, status,
                              requestslib_kwargs=None):
        """GET Services by Status

        :return: Response Object containing response code 200

        GET
        /admin/services?status
        """

        url = '{0}/admin/services?status={1}'.format(self.url, status)
        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

    def admin_migrate_domain(self, project_id, service_id, domain, new_cert,
                             requestslib_kwargs=None):
        """Update SAN domain

        :return: Response Object containing response code 202
        POST
        /admin/provider/akamai/service
        """

        url = '{0}/admin/provider/akamai/service'.format(self.url)
        request_object = requests.MigrateDomain(
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

    def get_flavor(self, flavor_location=None, flavor_id=None,
                   requestslib_kwargs=None):
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

        return self.request('GET', url,
                            requestslib_kwargs=requestslib_kwargs)

    def delete_flavor(self, flavor_location=None, flavor_id=None,
                      requestslib_kwargs=None):
        """Delete Flavor

        :return: Response Object containing response code 204
        DELETE
        flavors/{flavor_id}
        """
        if flavor_location:
            url = flavor_location
        else:
            url = u'{0}/flavors/{1}'.format(self.url, flavor_id)

        return self.request('DELETE', url,
                            requestslib_kwargs=requestslib_kwargs)

    def list_flavors(self, requestslib_kwargs=None):
        """List Flavors

        :return: Response Object containing response code 200 and body with
        list of flavors
        GET
        flavors
        """
        url = '{0}/flavors'.format(self.url)

        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

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
                    assert False, ("Aborted on status {0}").format(
                        current_status)
                    return service

            current_time = int(time.time())
            if current_time > stop_time:
                assert False, ('Timed out waiting for service status change'
                               ' to {0} after '
                               'waiting {1} seconds').format(status,
                                                             retry_timeout)

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
                    assert False, ("Aborted on status {0}").format(
                        current_status)
                    return resp

            current_time = int(time.time())
            if current_time > stop_time:
                assert False, ('Timed out waiting for service '
                               'to be deleted, after '
                               'waiting {0} seconds'.format(retry_timeout))

    def create_ssl_certificate(self, cert_type=None,
                               domain_name=None, flavor_id=None,
                               project_id=None,
                               requestslib_kwargs=None):
        """Creates SSL Certificate

        :return: Response Object containing response code 202

        POST
        ssl_certificate
        """
        url = '{0}/ssl_certificate'.format(self.url)

        requests_object = requests.CreateSSLCertificate(
            cert_type=cert_type,
            domain_name=domain_name,
            flavor_id=flavor_id,
            project_id=project_id
        )

        return self.request('POST', url, request_entity=requests_object,
                            requestslib_kwargs=requestslib_kwargs)

    def delete_ssl_certificate(self, cert_type=None,
                               domain_name=None, flavor_id=None,
                               requestslib_kwargs=None,):
        """Deletes SSL Certificate

        :return: Response Object containing response code 202

        DELETE
        ssl_certificate
        """

        url = '{0}/ssl_certificate/{1}'.format(self.url, domain_name)

        return self.request('DELETE', url,
                            requestslib_kwargs=requestslib_kwargs)

    def get_ssl_certificate(self,
                            domain_name,
                            requestslib_kwargs=None,):
        """GET SSL Certificate

        :return: Response Object containing response code 200 and body with
                details of certificate request

        GET
        ssl_certificate
        """

        url = '{0}/ssl_certificate/{1}'.format(self.url, domain_name)

        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

    def view_certificate_info(self,
                              san_cert_name,
                              requestslib_kwargs=None):
        """GET SSL Certificate Info

        :return: Response Object containing response code 200 and body with
                details of updated certificate info

        GET
        admin/provider/akamai/ssl_certificate/config/
        """

        url = '{0}/admin/provider/akamai/ssl_certificate/config/{1}'.format(
            self.url, san_cert_name)

        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

    def update_certificate_info(self,
                                san_cert_name,
                                spsId=None,
                                enabled=True,
                                requestslib_kwargs=None):
        """Update SSL Certificate Info

        :return: Response Object containing response code 200 and body with
                details of updated certificate info

        GET
        admin/provider/akamai/ssl_certificate/config/
        """

        url = '{0}/admin/provider/akamai/ssl_certificate/config/{1}'.format(
            self.url, san_cert_name)

        request_object = requests.PutSanCertConfigInfo(
            spsId=spsId,
            enabled=enabled)

        return self.request('POST', url,
                            request_entity=request_object,
                            requestslib_kwargs=requestslib_kwargs)

    def get_san_mapping_list(self, requestslib_kwargs=None):
        """GET SAN cert name - domain name mapping.

        :return: Response Object containing response code 200 and body with
                details of updated certificate info

        GET admin/provider/akamai/background_job/san_mapping
        """

        url = '{0}/admin/provider/akamai/background_job/san_mapping'.format(
            self.url
        )

        return self.request('GET', url, requestslib_kwargs=requestslib_kwargs)

    def put_san_mapping_list(self, san_mapping_list, requestslib_kwargs=None):
        """PUT SAN cert name - domain name mapping.

        :return: Response Object containing response code 200 and body with
                details of updated certificate info

        PUT admin/provider/akamai/background_job/san_mapping
        """

        url = '{0}/admin/provider/akamai/background_job/san_mapping'.format(
            self.url
        )

        return self.request(
            'PUT', url,
            data=json.dumps(san_mapping_list),
            requestslib_kwargs=requestslib_kwargs
        )
