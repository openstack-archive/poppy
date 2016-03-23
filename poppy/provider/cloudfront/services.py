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

from boto import cloudfront
from oslo_log import log

from poppy.common import decorators
from poppy.provider import base

LOG = log.getLogger(__name__)


class ServiceController(base.ServiceBase):
    """Base Service Controller Class."""

    @property
    def client(self):
        return self.driver.client

    def __init__(self, driver):
        super(ServiceController, self).__init__(driver)

        self.driver = driver

    # TODO(obulpathi): get service
    def get(self, service_name):
        return {'domains': [], 'origins': [], 'caching': []}

    # TODO(obulpathi): update service
    def update(self, service_name, service_obj):
        links = {}
        return self.responder.updated(service_name, links)

    def create(self, service_obj):
        # TODO(obulpathi): create a single distribution for multiple origins
        origin = service_obj.origins[0]
        LOG.info('Start creating cloudfront config for %s' % service_obj.name)
        try:
            # Create the origin for this domain:
            aws_origin = cloudfront.origin.CustomOrigin(
                dns_name=origin.origin,
                http_port=origin.port,
                # cannot specify ssl like this yet, CF takes a port #
                # https_port=origin.ssl,
                origin_protocol_policy='match-viewer')
            # TODO(tonytan4ever): Implement CF referrer restriction
            distribution = self.client.create_distribution(
                origin=aws_origin,
                enabled=True)
            if distribution.status == 'InProgress':
                status = 'deploy_in_progress'
            else:
                status = 'deployed'
        except cloudfront.exception.CloudFrontServerError as e:
            return self.responder.failed(str(e))
        except Exception as e:
            return self.responder.failed(str(e))

        links = [{'href': distribution.domain_name, 'rel': 'access_url'}]
        # extra information should be passed in here.
        LOG.info('Creating cloudfront config for %s'
                 'successful...' % service_obj.name)
        return self.responder.created(distribution.id, links, status=status)

    def delete(self, project_id, service_name):
        # NOTE(obulpathi): distribution_id is the equivalent of service_name
        distribution_id = service_name
        try:
            self.client.delete_distribution(distribution_id)

            return self.responder.deleted(distribution_id)
        except Exception as e:
            return self.responder.failed(str(e))

    def purge(self, distribution_id, hard=True, purge_url='/*'):
        # NOTE(tonytan4ever): boto does not have an API to efficiently
        # purge all urls yet
        try:
            purge_url = [] if purge_url is None else purge_url
            self.client.create_invalidation_request(distribution_id,
                                                    purge_url)
            return self.responder.purged(distribution_id,
                                         purge_url=purge_url)
        except Exception as e:
            return self.responder.failed(str(e))

    def get_provider_service_id(self, service_obj):
        return service_obj.name

    def get_metrics_by_domain(self, project_id, domain_name, regions,
                              **extras):
        '''Use CloudFronts's API to get the metrics by domain.'''
        return []

    @decorators.lazy_property(write=False)
    def current_customer(self):
        # TODO(tonytan4ever/obulpathi): Implement cloudfront's current_customer
        pass
