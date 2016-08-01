# Copyright (c) 2013 Rackspace, Inc.
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

import socket
import ssl
import sys

from kazoo import client
from OpenSSL import crypto
from oslo_log import log
import six

LOG = log.getLogger(__name__)

# Python 3 does not have ssl.PROTOCOL_SSLv2, but has PROTOCOL_TLSv1_1,
# PROTOCOL_TLSv1_2, and for some reason Jenkins will not pil up these
# new versions
try:
    if six.PY2:
        extra_versions = [ssl.PROTOCOL_SSLv2]    # pragma: no cover
    if six.PY3:                                  # pragma: no cover
        extra_versions = [ssl.PROTOCOL_TLSv1_1,  # pragma: no cover
                          ssl.PROTOCOL_TLSv1_2]  # pragma: no cover
except AttributeError:                           # pragma: no cover
    extra_versions = []                          # pragma: no cover

ssl_versions = [
    ssl.PROTOCOL_TLSv1,
    ssl.PROTOCOL_SSLv23
]

try:
    # Warning from python documentation "SSL version 3 is insecure.
    # Its use is highly discouraged."
    # https://docs.python.org/2/library/ssl.html#ssl.PROTOCOL_SSLv3
    ssl_versions.append(ssl.PROTOCOL_SSLv3)
except AttributeError:   # pragma: no cover
    pass                 # pragma: no cover

ssl_versions.extend(extra_versions)


def get_ssl_number_of_hosts(remote_host):
    """Get number of Alternative names for a (SAN) Cert."""

    LOG.info("Checking number of hosts for {0}".format(remote_host))
    for ssl_version in ssl_versions:
        try:
            cert = ssl.get_server_certificate((remote_host, 443),
                                              ssl_version=ssl_version)
        except ssl.SSLError:
            # This exception m
            continue

        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        sans = []
        for idx in range(0, x509.get_extension_count()):
            extension = x509.get_extension(idx)
            if extension.get_short_name() == 'subjectAltName':
                sans = [san.replace('DNS:', '') for san
                        in str(extension).split(',')]
                break

        # We can actually print all the Subject Alternative Names
        # for san in sans:
        #     print(san)
        result = len(sans)
        break
    else:
        raise ValueError(
            'Get remote host certificate {0} info failed.'.format(remote_host))
    return result


def get_sans_by_host(remote_host):
    """Get Subject Alternative Names for a (SAN) Cert."""

    LOG.info("Retrieving sans for {0}".format(remote_host))
    for ssl_version in ssl_versions:
        try:
            cert = ssl.get_server_certificate(
                (remote_host, 443),
                ssl_version=ssl_version
            )
        except ssl.SSLError:
            # This exception m
            continue

        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)

        sans = []
        for idx in range(0, x509.get_extension_count()):
            extension = x509.get_extension(idx)
            if extension.get_short_name() == 'subjectAltName':
                sans = [
                    san.replace('DNS:', '').strip() for san in
                    str(extension).split(',')
                ]
                break

        # accumulate all sans across multiple versions
        result = sans
        break
    else:
        raise ValueError(
            'Get remote host certificate {0} info failed.'.format(remote_host))
    return result


def _get_cert_alternate(remote_host):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET),
                               server_hostname=remote_host)
    conn.connect((remote_host, 443))
    cert = conn.getpeercert()

    conn.close()

    return cert


def get_ssl_number_of_hosts_alternate(remote_host):
    LOG.info("Checking number of hosts for {0}".format(remote_host))

    cert = _get_cert_alternate(remote_host)

    return len([
        san for record_type, san in cert['subjectAltName']
        if record_type == 'DNS'
    ])


def get_sans_by_host_alternate(remote_host):
    LOG.info("Retrieving sans for {0}".format(remote_host))

    cert = _get_cert_alternate(remote_host)

    return [
        san for record_type, san in cert['subjectAltName']
        if record_type == 'DNS'
    ]


def connect_to_zookeeper_storage_backend(conf):
    """Connect to a zookeeper cluster"""
    storage_backend_hosts = ','.join(['%s:%s' % (
        host, conf.storage_backend_port)
        for host in
        conf.storage_backend_host])
    zk_client = client.KazooClient(storage_backend_hosts)
    zk_client.start()
    return zk_client


def connect_to_zookeeper_queue_backend(conf):
    """Connect to a zookeeper cluster"""
    storage_backend_hosts = ','.join(['%s:%s' % (
        host, conf.queue_backend_port)
        for host in
        conf.queue_backend_host])
    zk_client = client.KazooClient(storage_backend_hosts)
    zk_client.start()
    return zk_client


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: %s <remote_host_you_want_get_cert_on>' % sys.argv[0])
        sys.exit(0)
    print("There are %s DNS names for SAN Cert on %s" % (
        get_ssl_number_of_hosts(sys.argv[1]), sys.argv[1]))
