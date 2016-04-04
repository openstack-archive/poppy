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

import datetime
import json

from oslo_log import log

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

                for san_cert_name in self.san_cert_cnames:
                    enabled = (
                        self.cert_info_storage.get_enabled_status(
                            san_cert_name
                        )
                    )
                    if not enabled:
                        continue
                    lastSpsId = (
                        self.cert_info_storage.get_cert_last_spsid(
                            san_cert_name
                        )
                    )
                    if lastSpsId not in [None, ""]:
                        LOG.info('Latest spsId for %s is: %s' % (san_cert_name,
                                                                 lastSpsId))
                        resp = self.sps_api_client.get(
                            self.sps_api_base_url.format(spsId=lastSpsId),
                        )
                        if resp.status_code != 200:
                            raise RuntimeError('SPS API Request Failed'
                                               'Exception: %s' % resp.text)
                        sps_request_info = json.loads(resp.text)[
                            'requestList'][0]
                        status = sps_request_info['status']
                        workFlowProgress = sps_request_info['workflowProgress']
                        if status == 'edge host already created or pending':
                            if workFlowProgress is not None and \
                                            'error' in workFlowProgress.lower():
                                LOG.info("SPS Pending with Error: {0}".format(
                                    workFlowProgress))
                                continue
                            else:
                                pass
                        elif status == 'CPS cancelled':
                            pass
                        elif status != 'SPS Request Complete':
                            LOG.info("SPS Not completed for %s..." %
                                     san_cert_name)
                            continue
                    # issue modify san_cert sps request
                    cert_info = self.cert_info_storage.get_cert_info(
                        san_cert_name)
                    cert_info['add.sans'] = cert_obj.domain_name
                    string_post_data = '&'.join(
                        ['%s=%s' % (k, v) for (k, v) in cert_info.items()])
                    LOG.info('Post modSan request with request data: %s' %
                             string_post_data)
                    resp = self.sps_api_client.post(
                        self.sps_api_base_url.format(spsId=""),
                        data=string_post_data.encode('utf-8')
                    )
                    if resp.status_code != 202:
                        raise RuntimeError('SPS Request failed.'
                                           'Exception: %s' % resp.text)
                    else:
                        resp_dict = json.loads(resp.text)
                        LOG.info('modSan request submitted. Response: %s' %
                                 str(resp_dict))
                        this_sps_id = resp_dict['spsId']
                        # get last item in results array and use its jobID
                        results = resp_dict['Results']['data']
                        this_job_id = results[0]['results']['jobID']
                        self.cert_info_storage.save_cert_last_ids(
                            san_cert_name,
                            this_sps_id,
                            this_job_id
                        )
                        self.san_mapping_queue.enqueue_san_mapping(
                            json.dumps({
                                'san_cert_domain': san_cert_name,
                                'domain_name': cert_obj.domain_name,
                            })
                        )
                        return self.responder.ssl_certificate_provisioned(
                            san_cert_name, {
                                'status': 'create_in_progress',
                                'san cert': san_cert_name,
                                'akamai_spsId': this_sps_id,
                                'created_at': str(datetime.datetime.now()),
                                'action': 'Waiting for customer domain '
                                          'validation for %s' %
                                          (cert_obj.domain_name)
                            })
                else:
                    self.mod_san_queue.enqueue_mod_san_request(
                        json.dumps(cert_obj.to_dict()))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': 'No available san cert for %s right now,'
                                  ' or no san cert info available. Support:'
                                  'Please write down the domain and keep an'
                                  ' eye on next available freed-up SAN certs.'
                                  ' More provisioning might be needed' %
                                  (cert_obj.domain_name)
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
