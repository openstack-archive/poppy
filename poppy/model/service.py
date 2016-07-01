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
import uuid

from poppy.model import common
from poppy.model.helpers import cachingrule
from poppy.model.helpers import domain
from poppy.model.helpers import origin
from poppy.model.helpers import provider_details
from poppy.model.helpers import restriction
from poppy.model import log_delivery as ld


VALID_STATUSES = [u'create_in_progress', u'deployed', u'update_in_progress',
                  u'delete_in_progress', u'failed']


class Service(common.DictSerializableModel):

    """Service Class."""

    def __init__(self,
                 service_id,
                 name,
                 domains,
                 origins,
                 flavor_id,
                 caching=[],
                 restrictions=[],
                 log_delivery=None,
                 operator_status='enabled',
                 project_id=''):
        self._service_id = str(service_id)
        self._name = name
        self._domains = domains
        self._origins = origins
        self._flavor_id = flavor_id
        self._caching = caching
        self._restrictions = restrictions
        self._log_delivery = log_delivery or ld.LogDelivery(False)
        self._status = 'create_in_progress'
        self._provider_details = {}
        self._operator_status = operator_status
        self._project_id = project_id

    @property
    def project_id(self):
        """Get project id."""
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value

    @property
    def service_id(self):
        """Get service id."""
        return self._service_id

    @service_id.setter
    def service_id(self, value):
        self._service_id = value

    @property
    def name(self):
        """Get or set name."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        """Get or set domains."""
        return self._domains

    @domains.setter
    def domains(self, value):
        self._domains = value

    @property
    def origins(self):
        """Get or set origins."""
        return self._origins

    @origins.setter
    def origins(self, value):
        self._origins = value

    @property
    def flavor_id(self):
        """Get or set flavor ref."""
        return self._flavor_id

    @flavor_id.setter
    def flavor_id(self, value):
        self._flavor_id = value

    @property
    def caching(self):
        """Get or set caching."""
        return self._caching

    @caching.setter
    def caching(self, value):
        self._caching = value

    @property
    def restrictions(self):
        """Get or set restrictions."""
        return self._restrictions

    @restrictions.setter
    def restrictions(self, value):
        self._restrictions = value

    @property
    def log_delivery(self):
        """Get log_delivery."""
        return self._log_delivery

    @log_delivery.setter
    def log_delivery(self, value):
        """Set log_delivery."""
        self._log_delivery = value

    @property
    def operator_status(self):
        """Get operator status."""
        return self._operator_status

    @operator_status.setter
    def operator_status(self, value):
        """Set operator status."""
        self._operator_status = value

    @property
    def status(self):
        """Get or set status.

        :returns boolean
        """
        # service status is a derived field
        # service will be in creating during service creation
        # if any of the provider services are still in 'deploy_in_progress'
        # status or 'failed' status, the poppy service is still in
        # 'creating' status.
        # if all provider services are in 'deployed' status. the poppy service
        # will be in 'deployed' status
        # if all provider services are in 'delete_in_progress' status.
        # the poppy service will be in 'delete_in_progress' status
        for provider_name in self.provider_details:
            provider_detail = self.provider_details[provider_name]
            if provider_detail.status == u'failed':
                self._status = u'failed'
                break
            elif provider_detail.status == u'delete_in_progress':
                self._status = u'delete_in_progress'
                break
            elif provider_detail.status == u'update_in_progress':
                self._status = u'update_in_progress'
            elif provider_detail.status == u'deploy_in_progress':
                self._status = u'create_in_progress'
        else:
            is_not_updating = (self._status != u'update_in_progress')
            if is_not_updating and self.provider_details != {}:
                self._status = 'deployed'

        return self._status

    @status.setter
    def status(self, value):
        if (value in VALID_STATUSES):
            self._status = value
        else:
            raise ValueError(
                u'Status {0} not in valid options: {1}'.format(
                    value,
                    VALID_STATUSES)
            )

    @property
    def provider_details(self):
        """Get or set provider details."""
        return self._provider_details

    @provider_details.setter
    def provider_details(self, value):
        self._provider_details = value

    @classmethod
    def init_from_dict(cls, project_id, input_dict):
        """Construct a model instance from a dictionary.

        This is only meant to be used for converting a
        response model into a model.
        When converting a model into a request model,
        use to_dict.
        """
        o = cls(service_id=uuid.uuid4(), name='unnamed',
                domains=[], origins=[], flavor_id='unnamed',
                project_id=project_id)
        domains = input_dict.get('domains', [])
        input_dict['domains'] = [domain.Domain.init_from_dict(d)
                                 for d in domains]
        origins = input_dict.get('origins', [])
        input_dict['origins'] = [origin.Origin.init_from_dict(og)
                                 for og in origins]

        caching_rules = input_dict.get('caching', [])
        input_dict['caching'] = [cachingrule.CachingRule.init_from_dict(cr)
                                 for cr in caching_rules]

        restrictions = input_dict.get('restrictions', [])
        input_dict['restrictions'] = [restriction.Restriction.init_from_dict(r)
                                      for r in restrictions]

        pds = input_dict.get('provider_details', {})
        for provider_name in pds:
            pd = pds[provider_name]
            input_dict['provider_details'][provider_name] = (
                provider_details.ProviderDetail.init_from_dict(pd))

        log_delivery = input_dict.get('log_delivery', {})

        input_dict['log_delivery'] = ld.LogDelivery.init_from_dict(
            log_delivery)

        o.from_dict(input_dict)
        return o

    def to_dict(self):
        """Construct a model instance from a dictionary.

        This is only meant to be used for converting a
        response model into a model.
        When converting a model into a request model,
        use to_dict.
        """
        result = common.DictSerializableModel.to_dict(self)
        # need to deserialize the nested object
        domain_obj_list = result['domains']
        result['domains'] = [d.to_dict() for d in domain_obj_list]
        # could possibly need to add domain_certificate_status in here

        origin_obj_list = result['origins']
        result['origins'] = [o.to_dict() for o in origin_obj_list]

        restrictions_obj_list = result['restrictions']
        result['restrictions'] = [r.to_dict() for r in restrictions_obj_list]

        caching_obj_list = result['caching']
        result['caching'] = [c.to_dict() for c in caching_obj_list]

        provider_details = result['provider_details']
        new_provider_details = {}
        for provider in provider_details:
            new_provider_details[provider] = (
                provider_details[provider].to_dict())
        result['provider_details'] = new_provider_details
        result['log_delivery'] = result['log_delivery'].to_dict()

        return result
