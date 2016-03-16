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

from cafe.engine.models import base


class CreateService(base.AutoMarshallingModel):
    """Marshalling for Create Service requests."""

    def __init__(self, service_name=None, domain_list=None, origin_list=None,
                 caching_list=None, restrictions_list=None, flavor_id=None,
                 log_delivery=None):
        super(CreateService, self).__init__()

        self.service_name = service_name
        self.domain_list = domain_list or []
        self.origin_list = origin_list or []
        self.caching_list = caching_list or []
        self.restrictions_list = restrictions_list or []
        self.flavor_id = flavor_id
        self.log_delivery = log_delivery or {"enabled": False}

    def _obj_to_json(self):
        create_service_request = {"name": self.service_name,
                                  "domains": self.domain_list,
                                  "origins": self.origin_list,
                                  "caching": self.caching_list,
                                  "restrictions": self.restrictions_list,
                                  "flavor_id": self.flavor_id,
                                  "log_delivery": self.log_delivery}
        return json.dumps(create_service_request)


class PatchService(base.AutoMarshallingModel):
    """Marshalling for Patch Service requests."""

    def __init__(self, request_body=None):
        super(PatchService, self).__init__()

        self.request_body = request_body

    def _obj_to_json(self):
        patch_service_request = self.request_body
        return json.dumps(patch_service_request)


class ServiceAction(base.AutoMarshallingModel):
    """Marshalling for Action on Services requests."""

    def __init__(self, action, project_id=None, domain=None):
        super(ServiceAction, self).__init__()

        self.project_id = project_id
        self.action = action
        self.domain = domain

    def _obj_to_json(self):
        service_action_request = {
            "action": self.action
        }
        if self.domain:
            service_action_request["domain"] = self.domain
        elif self.project_id:
            service_action_request["project_id"] = self.project_id
        return json.dumps(service_action_request)


class ServiceStatus(base.AutoMarshallingModel):
    """Marshalling for Action on Services status requests."""

    def __init__(self, status, project_id, service_id):
        super(ServiceStatus, self).__init__()

        self.status = status
        self.project_id = project_id
        self.service_id = service_id

    def _obj_to_json(self):
        service_status_request = {
            "status": self.status,
            "project_id": self.project_id,
            "service_id": self.service_id
        }

        return json.dumps(service_status_request)


class ServiceLimit(base.AutoMarshallingModel):
    """Marshalling for Service Limit requests."""

    def __init__(self, limit=None):
        super(ServiceLimit, self).__init__()
        self.limit = limit

    def _obj_to_json(self):
        service_limit_request = {}
        if self.limit:
            service_limit_request["limit"] = self.limit
        return json.dumps(service_limit_request)


class MigrateDomain(base.AutoMarshallingModel):
    """Marshalling for Action on Services requests."""

    def __init__(self, project_id, service_id, domain, new_cert):
        super(MigrateDomain, self).__init__()

        self.project_id = project_id
        self.service_id = service_id
        self.domain = domain
        self.new_cert = new_cert

    def _obj_to_json(self):
        service_action_request = {
            "project_id": self.project_id,
            "service_id": self.service_id,
            "domain_name": self.domain,
            "new_cert": self.new_cert
        }
        return json.dumps(service_action_request)


class CreateFlavor(base.AutoMarshallingModel):
    """Marshalling for Create Flavor requests."""

    def __init__(self, flavor_id=None, provider_list=None, limits=None):
        super(CreateFlavor, self).__init__()

        self.flavor_id = flavor_id
        self.provider_list = provider_list
        self.limits = limits

    def _obj_to_json(self):
        create_flavor_request = {"id": self.flavor_id,
                                 "providers": self.provider_list,
                                 "limits": self.limits}
        return json.dumps(create_flavor_request)


class CreateSSLCertificate(base.AutoMarshallingModel):
    """Marshalling for Create SSL Certificate requests."""

    def __init__(self, cert_type=None, domain_name=None, flavor_id=None,
                 project_id=None):
        super(CreateSSLCertificate, self).__init__()

        self.cert_type = cert_type
        self.domain_name = domain_name
        self.flavor_id = flavor_id
        self.project_id = project_id

    def _obj_to_json(self):
        create_ssl_certificate_request = {
            "cert_type": self.cert_type,
            "domain_name": self.domain_name,
            "flavor_id": self.flavor_id,
            "project_id": self.project_id
        }
        return json.dumps(create_ssl_certificate_request)


class PutSanCertConfigInfo(base.AutoMarshallingModel):
    """Marshalling for Create SSL Certificate requests."""

    def __init__(self, spsId=None, enabled=True):
        super(PutSanCertConfigInfo, self).__init__()

        self.spsId = spsId
        self.enabled = enabled

    def _obj_to_json(self):
        put_san_cert_info_request = {
            "spsId": self.spsId,
            "enabled": self.enabled
        }
        return json.dumps(put_san_cert_info_request)
