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

import copy
import datetime
import json

from oslo_log import log

from poppy.provider.akamai import utils
from poppy.provider import base

LOG = log.getLogger(__name__)


class CertificateController(base.CertificateBase):

    @property
    def mod_san_queue(self):
        return self.driver.mod_san_queue

    @property
    def san_cert_cnames(self):
        return self.driver.san_cert_cnames

    @property
    def cert_info_storage(self):
        return self.driver.cert_info_storage

    @property
    def san_mapping_queue(self):
        return self.driver.san_mapping_queue

    @property
    def sps_api_client(self):
        return self.driver.akamai_sps_api_client

    def __init__(self, driver):
        super(CertificateController, self).__init__(driver)

        self.driver = driver
        self.sps_api_base_url = self.driver.akamai_sps_api_base_url

    def create_certificate(self, cert_obj, enqueue=True):
        if cert_obj.cert_type == 'san':
            try:
                found, found_cert = (
                    self._check_domain_already_exists_on_san_certs(
                        cert_obj.domain_name
                    )
                )
                if found is True:
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'failed',
                        'san cert': None,
                        'created_at': str(datetime.datetime.now()),
                        'action': (
                            'Domain {0} already exists '
                            'on san cert {1}.'.format(
                                cert_obj.domain_name, found_cert
                            )
                        )
                    })

                if enqueue:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': (
                            'San cert request for {0} has been '
                            'enqueued.'.format(cert_obj.domain_name)
                        )
                    })

                san_cert_hostname_limit = (
                    self.cert_info_storage.get_san_cert_hostname_limit()
                )

                for san_cert_name in self.san_cert_cnames:
                    enabled = (
                        self.cert_info_storage.get_enabled_status(
                            san_cert_name
                        )
                    )
                    if not enabled:
                        continue

                    # if the limit provided as an arg to this function is None
                    # default san_cert_hostname_limit to the value provided in
                    # the config file.
                    san_cert_hostname_limit = (
                        san_cert_hostname_limit or
                        self.driver.san_cert_hostname_limit
                    )

                    # Check san_cert to enforce number of hosts hasn't
                    # reached the limit. If the current san_cert is at max
                    # capacity continue to the next san_cert
                    san_hosts = utils.get_ssl_number_of_hosts(
                        '.'.join(
                            [
                                san_cert_name,
                                self.driver.akamai_https_access_url_suffix
                            ]
                        )
                    )
                    if san_hosts >= san_cert_hostname_limit:
                        continue

                    last_sps_id = (
                        self.cert_info_storage.get_cert_last_spsid(
                            san_cert_name
                        )
                    )
                    if last_sps_id not in [None, ""]:
                        LOG.info('Latest spsId for {0} is: {1}'.format(
                            san_cert_name,
                            last_sps_id)
                        )
                        resp = self.sps_api_client.get(
                            self.sps_api_base_url.format(spsId=last_sps_id),
                        )
                        if resp.status_code != 200:
                            raise RuntimeError(
                                'SPS API Request Failed. '
                                'Exception: {0}'.format(resp.text)
                            )
                        sps_request_info = json.loads(resp.text)[
                            'requestList'][0]
                        status = sps_request_info['status']
                        work_flow_progress = (
                            sps_request_info['workflowProgress']
                        )
                        if status == 'edge host already created or pending':
                            if work_flow_progress is not None and \
                                    'error' in work_flow_progress.lower():
                                LOG.info("SPS Pending with Error: {0}".format(
                                    work_flow_progress))
                                continue
                            else:
                                pass
                        elif status == 'CPS cancelled':
                            pass
                        elif status != 'SPS Request Complete':
                            LOG.info("SPS Not completed for {0}...".format(
                                     san_cert_name))
                            continue
                    # issue modify san_cert sps request
                    cert_info = self.cert_info_storage.get_cert_info(
                        san_cert_name)
                    cert_info['add.sans'] = cert_obj.domain_name
                    string_post_data = '&'.join(
                        ['%s=%s' % (k, v) for (k, v) in cert_info.items()])
                    LOG.info(
                        'Post modSan request with request data: {0}'.format(
                            string_post_data
                        )
                    )
                    resp = self.sps_api_client.post(
                        self.sps_api_base_url.format(spsId=""),
                        data=string_post_data.encode('utf-8')
                    )
                    if resp.status_code != 202:
                        raise RuntimeError(
                            'SPS Request failed. '
                            'Exception: {0}'.format(resp.text)
                        )
                    else:
                        resp_dict = json.loads(resp.text)
                        LOG.info(
                            'modSan request submitted. Response: {0}'.format(
                                resp_dict
                            )
                        )
                        this_sps_id = resp_dict['spsId']
                        # get last item in results array and use its jobID
                        results = resp_dict['Results']['data']
                        this_job_id = results[0]['results']['jobID']
                        self.cert_info_storage.save_cert_last_ids(
                            san_cert_name,
                            this_sps_id,
                            this_job_id
                        )
                        cert_copy = copy.deepcopy(cert_obj.to_dict())
                        (
                            cert_copy['cert_details']
                            [self.driver.provider_name]
                        ) = {
                            'extra_info': {
                                'akamai_spsId': this_sps_id,
                                'san cert': san_cert_name
                            }
                        }

                        self.san_mapping_queue.enqueue_san_mapping(
                            json.dumps(cert_copy)
                        )
                        return self.responder.ssl_certificate_provisioned(
                            san_cert_name, {
                                'status': 'create_in_progress',
                                'san cert': san_cert_name,
                                'akamai_spsId': this_sps_id,
                                'created_at': str(datetime.datetime.now()),
                                'action': 'Waiting for customer domain '
                                          'validation for {0}'.format(
                                    cert_obj.domain_name)
                            })
                else:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': 'No available san cert for {0} right now,'
                                  ' or no san cert info available. Support:'
                                  'Please write down the domain and keep an'
                                  ' eye on next available freed-up SAN certs.'
                                  ' More provisioning might be needed'.format(
                            cert_obj.domain_name)
                    })
            except Exception as e:
                LOG.exception(
                    "Error {0} during certificate creation for {1} "
                    "sending the request sent back to the queue.".format(
                        e, cert_obj.domain_name
                    )
                )
                try:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': (
                            'San cert request for {0} has been '
                            'enqueued.'.format(cert_obj.domain_name)
                        )
                    })
                except Exception as exc:
                    LOG.exception("Unable to enqueue {0}, Error: {1}".format(
                        cert_obj.domain_name,
                        exc
                    ))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'failed',
                        'san cert': None,
                        'created_at': str(datetime.datetime.now()),
                        'action': 'Waiting for action... Provision '
                                  'san cert failed for {0} failed.'.format(
                            cert_obj.domain_name)
                    })
        else:
            return self.responder.ssl_certificate_provisioned(None, {
                'status': 'failed',
                'reason': "Cert type : {0} hasn't been implemented".format(
                    cert_obj.cert_type
                )
            })

    def _check_domain_already_exists_on_san_certs(self, domain_name):
        """Check all configured san certs for domain."""

        found = False
        found_cert = None
        for san_cert_name in self.san_cert_cnames:
            sans = utils.get_sans_by_host(
                '.'.join(
                    [
                        san_cert_name,
                        self.driver.akamai_https_access_url_suffix
                    ]
                )
            )
            if domain_name in sans:
                found = True
                found_cert = san_cert_name
                break

        return found, found_cert
