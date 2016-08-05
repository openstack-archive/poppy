# Copyright (c) 2016 Rackspace, Inc.
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

from cassandra import query
from oslo_log import log
from six.moves import filterfalse

from poppy.model import ssl_certificate
from poppy.storage import base


LOG = log.getLogger(__name__)

CQL_CREATE_CERT = '''
    INSERT INTO certificate_info (project_id,
        flavor_id,
        cert_type,
        domain_name,
        cert_details
        )
    VALUES (%(project_id)s,
        %(flavor_id)s,
        %(cert_type)s,
        %(domain_name)s,
        %(cert_details)s)
'''

CQL_SEARCH_CERT_BY_DOMAIN = '''
    SELECT project_id,
        flavor_id,
        cert_type,
        domain_name,
        cert_details
    FROM certificate_info
    WHERE domain_name = %(domain_name)s
'''

CQL_GET_CERTS_BY_STATUS = '''
    SELECT domain_name
    FROM cert_status WHERE status = %(status)s
'''

CQL_DELETE_CERT = '''
    DELETE FROM certificate_info
    WHERE domain_name = %(domain_name)s
'''

CQL_DELETE_CERT_STATUS = '''
    DELETE FROM cert_status
    WHERE domain_name = %(domain_name)s
'''


CQL_INSERT_CERT_STATUS = '''
    INSERT INTO cert_status (domain_name,
        status
        )
    VALUES (%(domain_name)s,
        %(status)s)
'''

CQL_UPDATE_CERT_DETAILS = '''
    UPDATE certificate_info
    set cert_details = %(cert_details)s
    WHERE domain_name = %(domain_name)s
    IF cert_type = %(cert_type)s AND flavor_id = %(flavor_id)s
'''


class CertificatesController(base.CertificatesController):

    """Certificates Controller."""

    @property
    def session(self):
        """Get session.

        :returns session
        """
        return self._driver.database

    def create_certificate(self, project_id, cert_obj):
        if self.cert_already_exist(domain_name=cert_obj.domain_name,
                                   comparing_cert_type=cert_obj.cert_type,
                                   comparing_flavor_id=cert_obj.flavor_id,
                                   comparing_project_id=project_id):
            raise ValueError('Certificate already exists '
                             'for {0} '.format(cert_obj.domain_name))

        args = {
            'project_id': project_id,
            'flavor_id': cert_obj.flavor_id,
            'cert_type': cert_obj.cert_type,
            'domain_name': cert_obj.domain_name,
            # when create the cert, cert domain has not been assigned yet
            # In future we can tweak the logic to assign cert_domain
            # 'cert_domain': '',
            'cert_details': cert_obj.cert_details
        }
        stmt = query.SimpleStatement(
            CQL_CREATE_CERT,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, args)

        try:
            provider_status = json.loads(
                list(cert_obj.cert_details.values())[0]
            )
            cert_status = provider_status['extra_info']['status']
        except (IndexError, IndexError, ValueError) as e:
            LOG.error("Certificate details in inconsistent "
                      "state: {0}".format(cert_obj.cert_details))
            LOG.error(e)
        else:
            # insert/update for cassandra
            self.insert_cert_status(cert_obj.domain_name, cert_status)

    def delete_certificate(self, project_id, domain_name, cert_type):
        args = {
            'domain_name': domain_name.lower()
        }

        stmt = query.SimpleStatement(
            CQL_SEARCH_CERT_BY_DOMAIN,
            consistency_level=self._driver.consistency_level)
        result_set = self.session.execute(stmt, args)
        complete_results = list(result_set)
        if complete_results:
            for r in complete_results:
                r_project_id = str(r.get('project_id'))
                r_cert_type = str(r.get('cert_type'))
                if r_project_id == str(project_id) and \
                        r_cert_type == str(cert_type):
                    args = {
                        'domain_name': str(r.get('domain_name'))
                    }
                    stmt = query.SimpleStatement(
                        CQL_DELETE_CERT,
                        consistency_level=self._driver.consistency_level)
                    self.session.execute(stmt, args)
                    stmt = query.SimpleStatement(
                        CQL_DELETE_CERT_STATUS,
                        consistency_level=self._driver.consistency_level)
                    self.session.execute(stmt, args)
        else:
            raise ValueError(
                "No certificate found for: {0},"
                "type: {1}".format(domain_name, cert_type))

    def update_certificate(self, domain_name, cert_type, flavor_id,
                           cert_details):

        args = {
            'domain_name': domain_name,
            'cert_type': cert_type,
            'flavor_id': flavor_id,
            'cert_details': cert_details
        }
        stmt = query.SimpleStatement(
            CQL_UPDATE_CERT_DETAILS,
            consistency_level=self._driver.consistency_level)
        self.session.execute(stmt, args)

        try:
            provider_status = json.loads(list(cert_details.values())[0])
            cert_status = provider_status['extra_info']['status']
        except (IndexError, IndexError, ValueError) as e:
            LOG.error("Certificate details in inconsistent "
                      "state: {0}".format(cert_details))
            LOG.error(e)
        else:
            # insert/update for cassandra
            self.insert_cert_status(domain_name, cert_status)

    def insert_cert_status(self, domain_name, cert_status):
            cert_args = {
                'domain_name': domain_name,
                'status': cert_status
            }
            stmt = query.SimpleStatement(
                CQL_INSERT_CERT_STATUS,
                consistency_level=self._driver.consistency_level)
            self.session.execute(stmt, cert_args)

    def get_certs_by_status(self, status):

        LOG.info("Getting domains which have "
                 "certificate in status : {0}".format(status))
        args = {
            'status': status
        }
        stmt = query.SimpleStatement(
            CQL_GET_CERTS_BY_STATUS,
            consistency_level=self._driver.consistency_level)
        resultset = self.session.execute(stmt, args)
        complete_results = list(resultset)

        return complete_results

    def get_certs_by_domain(self, domain_name, project_id=None,
                            flavor_id=None,
                            cert_type=None):

        LOG.info("Check if cert on '{0}' exists".format(domain_name))
        args = {
            'domain_name': domain_name.lower()
        }
        stmt = query.SimpleStatement(
            CQL_SEARCH_CERT_BY_DOMAIN,
            consistency_level=self._driver.consistency_level)
        resultset = self.session.execute(stmt, args)
        complete_results = list(resultset)
        certs = []
        if complete_results:
            for r in complete_results:
                r_project_id = str(r.get('project_id'))
                r_flavor_id = str(r.get('flavor_id'))
                r_cert_type = str(r.get('cert_type'))
                r_cert_details = {}
                # in case cert_details is None
                cert_details = r.get('cert_details', {}) or {}
                # Need to convert cassandra dict into real dict
                # And the value of cert_details is a string dict
                for key in cert_details:
                    r_cert_details[key] = json.loads(cert_details[key])
                LOG.info(
                    "Certificate for domain: {0}  with flavor_id: {1}, "
                    "cert_details : {2} and  cert_type: {3} present "
                    "on project_id: {4}".format(
                        domain_name,
                        r_flavor_id,
                        r_cert_details,
                        r_cert_type,
                        r_project_id
                    )
                )
                ssl_cert = ssl_certificate.SSLCertificate(
                    domain_name=domain_name,
                    flavor_id=r_flavor_id,
                    cert_details=r_cert_details,
                    cert_type=r_cert_type,
                    project_id=r_project_id
                )

                certs.append(ssl_cert)

        non_none_attrs_gen = filterfalse(
            lambda x: list(x.values())[0] is None, [{'project_id': project_id},
                                                    {'flavor_id': flavor_id},
                                                    {'cert_type': cert_type}])
        non_none_attrs_list = list(non_none_attrs_gen)
        non_none_attrs_dict = {}

        if non_none_attrs_list:
            for attr in non_none_attrs_list:
                non_none_attrs_dict.update(attr)

        def argfilter(certificate):
            all_conditions = True
            if non_none_attrs_dict:
                for k, v in non_none_attrs_dict.items():
                    if getattr(certificate, k) != v:
                        all_conditions = False

            return all_conditions

        total_certs = [cert for cert in certs if argfilter(cert)]

        if len(total_certs) == 1:
            return total_certs[0]
        else:
            return total_certs

    def cert_already_exist(self, domain_name, comparing_cert_type,
                           comparing_flavor_id, comparing_project_id):
        """cert_already_exist

        Check if a cert with this domain name and type has already been
        created, or if the domain has been taken by other customers

        :param domain_name
        :param comparing_cert_type
        :param comparing_flavor_id
        :param comparing_project_id

        :returns Boolean if the cert with same type exists with another user.
        """
        cert = self.get_certs_by_domain(
            domain_name=domain_name,
            cert_type=comparing_cert_type,
            flavor_id=comparing_flavor_id
        )

        if cert:
            return True
        else:
            return False
