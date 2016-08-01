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
from six.moves import urllib

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
    def sni_cert_cnames(self):
        return self.driver.sni_cert_cnames

    @property
    def cert_info_storage(self):
        return self.driver.cert_info_storage

    @property
    def san_mapping_queue(self):
        return self.driver.san_mapping_queue

    @property
    def sps_api_client(self):
        return self.driver.akamai_sps_api_client

    @property
    def cps_api_client(self):
        return self.driver.akamai_cps_api_client

    def __init__(self, driver):
        super(CertificateController, self).__init__(driver)

        self.driver = driver
        self.sps_api_base_url = self.driver.akamai_sps_api_base_url
        self.cps_api_base_url = self.driver.akamai_cps_api_base_url

    def create_certificate(self, cert_obj, enqueue=True, https_upgrade=False):
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
                    extras = {
                        'status': 'create_in_progress',
                        'san cert': None,
                        # Add logging so it is easier for testing
                        'created_at': str(datetime.datetime.now()),
                        'action': (
                            'San cert request for {0} has been '
                            'enqueued.'.format(cert_obj.domain_name)
                        )
                    }
                    if https_upgrade is True:
                        extras['https upgrade notes'] = (
                            "This domain was upgraded from HTTP to HTTPS SAN."
                            "Take note of the domain name. Where applicable, "
                            "delete the old HTTP policy after the upgrade is "
                            "complete or the old policy is no longer in use."
                        )
                    return self.responder.ssl_certificate_provisioned(
                        None,
                        extras
                    )

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
        elif cert_obj.cert_type == 'sni':
            # create a DV SAN SNI certificate using Akamai CPS API
            return self.create_sni_certificate(
                cert_obj, enqueue, https_upgrade)
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

    def _check_domain_already_exists_on_sni_certs(self, domain_name):
        """Check all configured sni certs for domain."""

        found = False
        found_cert = None
        for sni_cert_name in self.sni_cert_cnames:
            sans = utils.get_sans_by_host_alternate(sni_cert_name)
            if domain_name in sans:
                found = True
                found_cert = sni_cert_name
                break

        return found, found_cert

    def create_sni_certificate(self, cert_obj, enqueue, https_upgrade):
        try:
            found, found_cert = (
                self._check_domain_already_exists_on_sni_certs(
                    cert_obj.domain_name
                )
            )
            if found is True:
                return self.responder.ssl_certificate_provisioned(None, {
                    'status': 'failed',
                    'sni_cert': None,
                    'created_at': str(datetime.datetime.now()),
                    'action': (
                        'Domain {0} already exists '
                        'on sni cert {1}.'.format(
                            cert_obj.domain_name, found_cert
                        )
                    )
                })
            if enqueue:
                self.mod_san_queue.enqueue_mod_san_request(
                    json.dumps(cert_obj.to_dict()))
                extras = {
                    'status': 'create_in_progress',
                    'sni_cert': None,
                    # Add logging so it is easier for testing
                    'created_at': str(datetime.datetime.now()),
                    'action': (
                        'SNI cert request for {0} has been '
                        'enqueued.'.format(cert_obj.domain_name)
                    )
                }
                if https_upgrade is True:
                    extras['https upgrade notes'] = (
                        "This domain was upgraded from HTTP to HTTPS SNI."
                        "Take note of the domain name. Where applicable, "
                        "delete the old HTTP policy after the upgrade is "
                        "complete or the old policy is no longer in use."
                    )
                return self.responder.ssl_certificate_provisioned(
                    None,
                    extras
                )
            cert_hostname_limit = (
                self.cert_info_storage.get_san_cert_hostname_limit()
            )
            for cert_name in self.sni_cert_cnames:
                cert_hostname_limit = (
                    cert_hostname_limit or
                    self.driver.san_cert_hostname_limit
                )

                host_names_count = utils.get_ssl_number_of_hosts_alternate(
                    cert_name
                )
                if host_names_count >= cert_hostname_limit:
                    continue

                try:
                    enrollment_id = (
                        self.cert_info_storage.get_cert_enrollment_id(
                            cert_name))
                    # GET the enrollment by ID
                    headers = {
                        'Accept': ('application/vnd.akamai.cps.enrollment.v1+'
                                   'json')
                    }
                    resp = self.cps_api_client.get(
                        self.cps_api_base_url.format(
                            enrollmentId=enrollment_id),
                        headers=headers
                    )
                    if resp.status_code not in [200, 202]:
                        raise RuntimeError(
                            'CPS Request failed. Unable to GET enrollment '
                            'with id {0} Exception: {1}'.format(
                                enrollment_id, resp.text))
                    resp_json = json.loads(resp.text)
                    # check enrollment does not have any pending changes
                    if len(resp_json['pendingChanges']) > 0:
                        LOG.info("{0} has pending changes, skipping...".format(
                            cert_name))
                        continue

                    # adding sans should get them cloned into sni host names
                    resp_json['csr']['sans'] = resp_json['csr']['sans'].append(
                        cert_obj.domain_name
                    )

                    # PUT the enrollment including the modifications
                    headers = {
                        'Content-Type': (
                            'application/vnd.akamai.cps.enrollment.v1+json'),
                        'Accept': (
                            'application/vnd.akamai.cps.enrollment-status.v1+'
                            'json')
                    }
                    resp = self.cps_api_client.put(
                        self.cps_api_base_url.format(
                            enrollmentId=enrollment_id),
                        data=json.dumps(resp_json),
                        headers=headers
                    )
                    if resp.status_code not in [200, 202]:
                        raise RuntimeError(
                            'CPS Request failed. Unable to modify enrollment '
                            'with id {0} Exception: {1}'.format(
                                enrollment_id, resp.text))

                    # resp code 200 means PUT didn't create a change
                    # resp code 202 means PUT created a change
                    if resp.status_code == 202:
                        # save the change id for future reference
                        change_url = json.loads(resp.text)['changes'][0]
                        cert_copy = copy.deepcopy(cert_obj.to_dict())
                        (
                            cert_copy['cert_details']
                            [self.driver.provider_name]
                        ) = {
                            'extra_info': {
                                'change_url': change_url,
                                'sni_cert': cert_name
                            }
                        }
                        self.san_mapping_queue.enqueue_san_mapping(
                            json.dumps(cert_copy)
                        )
                        return self.responder.ssl_certificate_provisioned(
                            cert_name, {
                                'status': 'create_in_progress',
                                'sni_cert': cert_name,
                                'change_url': change_url,
                                'created_at': str(datetime.datetime.now()),
                                'action': 'Waiting for customer domain '
                                          'validation for {0}'.format(
                                    cert_obj.domain_name)
                            })
                except Exception as exc:
                    LOG.exception(
                        "Unable to provision certificate {0}, "
                        "Error: {1}".format(cert_obj.domain_name, exc))
                    return self.responder.ssl_certificate_provisioned(None, {
                        'status': 'failed',
                        'sni_cert': None,
                        'created_at': str(datetime.datetime.now()),
                        'action': 'Waiting for action... CPS API provision '
                                  'DV SNI cert failed for {0} failed.'.format(
                            cert_obj.domain_name)
                    })
            else:
                self.mod_san_queue.enqueue_mod_san_request(
                    json.dumps(cert_obj.to_dict()))
                return self.responder.ssl_certificate_provisioned(None, {
                    'status': 'create_in_progress',
                    'sni_cert': None,
                    # Add logging so it is easier for testing
                    'created_at': str(datetime.datetime.now()),
                    'action': 'No available sni cert for {0} right now,'
                              ' or no sni cert info available. Support:'
                              'Please write down the domain and keep an'
                              ' eye on next available freed-up SNI certs.'
                              ' More provisioning might be needed'.format(
                        cert_obj.domain_name)
                })
        except Exception as e:
            LOG.exception(
                "Error {0} during SNI certificate creation for {1} "
                "sending the request sent back to the queue.".format(
                    e, cert_obj.domain_name
                )
            )
            try:
                self.mod_san_queue.enqueue_mod_san_request(
                    json.dumps(cert_obj.to_dict()))
                return self.responder.ssl_certificate_provisioned(None, {
                    'status': 'create_in_progress',
                    'sni_cert': None,
                    # Add logging so it is easier for testing
                    'created_at': str(datetime.datetime.now()),
                    'action': (
                        'SNI cert request for {0} has been '
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
                    'sni_cert': None,
                    'created_at': str(datetime.datetime.now()),
                    'action': 'Waiting for action... Provision '
                              'sni cert failed for {0} failed.'.format(
                        cert_obj.domain_name)
                })

    def delete_certificate(self, cert_obj):
        if cert_obj.cert_type == 'sni':
            # get change id
            first_provider_cert_details = (
                list(cert_obj.cert_details.values())[0].get("extra_info", None)
            )
            change_url = first_provider_cert_details.get('change_url')

            if first_provider_cert_details is None or change_url is None:
                return self.responder.ssl_certificate_deleted(
                    cert_obj.domain_name,
                    {
                        'status': 'failed',
                        'reason': (
                            'Cert is missing details required for delete '
                            'operation {0}.'.format(
                                first_provider_cert_details)
                        )
                    }
                )

            headers = {
                'Accept': 'application/vnd.akamai.cps.change-id.v1+json'
            }

            akamai_change_url = urllib.parse.urljoin(
                str(self.driver.akamai_conf.policy_api_base_url),
                change_url
            )

            # delete call to cps api to cancel the change
            resp = self.cps_api_client.delete(
                akamai_change_url,
                headers=headers
            )
            if resp.status_code != 200:
                LOG.error(
                    "Certificate delete for {0} failed. "
                    "Status code {1}. Response {2}.".format(
                        cert_obj.domain_name,
                        resp.status_code,
                        resp.text,
                    ))
                return self.responder.ssl_certificate_deleted(
                    cert_obj.domain_name,
                    {
                        'status': 'failed',
                        'reason': 'Delete request for {0} failed.'.format(
                            cert_obj.domain_name)
                    }
                )
            else:
                LOG.info(
                    "Successfully cancelled {0}, {1}".format(
                        cert_obj.domain_name,
                        resp.text)
                )
                return self.responder.ssl_certificate_deleted(
                    cert_obj.domain_name,
                    {
                        'status': 'deleted',
                        'deleted_at': str(datetime.datetime.now()),
                        'reason': 'Delete request for {0} succeeded.'.format(
                            cert_obj.domain_name)
                    }
                )
        else:
            return self.responder.ssl_certificate_provisioned(None, {
                'status': 'ignored',
                'reason': "Delete cert type {0} not supported.".format(
                    cert_obj.cert_type
                )
            })
