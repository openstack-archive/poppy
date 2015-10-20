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

AVAILABLE_PROTOCOLS = [
    u'http',
    u'https']

CERTIFICATE_OPTIONS = [
    None,
    u'shared',
    u'san',
    u'custom']

from poppy.model import common


class Domain(common.DictSerializableModel):

    def __init__(self, domain, protocol='http',
                 certificate=None):
        self._domain = domain.lower().strip()

        if (protocol in AVAILABLE_PROTOCOLS):
            self._protocol = protocol
        else:
            raise ValueError(
                u'Protocol: {0} not in currently available'
                ' protocols: {1}'.format(
                    protocol,
                    AVAILABLE_PROTOCOLS)
            )

        # certificate option only effective when protocol is https
        self._certificate = certificate
        if self._protocol == 'https':
            if self._certificate not in CERTIFICATE_OPTIONS:
                raise ValueError(
                    u'Certificate option: {0} is not valid.'
                    'Valid certificate options are: {1}'.format(
                        certificate,
                        CERTIFICATE_OPTIONS)
                )

    @property
    def domain(self):
        """domain.

        :returns domain
        """
        return self._domain

    @domain.setter
    def domain(self, value):
        """domain setter."""
        self._domain = value.lower().strip()

    @property
    def certificate(self):
        """certificate option.

        :returns certificate
        """
        return self._certificate

    @certificate.setter
    def certificate(self, value):
        """domain certificate setter."""
        if self._protocol != 'https':
            raise ValueError('Cannot set certificate option for'
                             ' non-https domain')
        if value not in CERTIFICATE_OPTIONS:
            raise ValueError(
                u'Certificate option: {0} is not valid.'
                'Valid certificate options are: {1}'.format(
                    value,
                    CERTIFICATE_OPTIONS)
            )
        self._certificate = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if (value in AVAILABLE_PROTOCOLS):
            self._protocol = value
        else:
            raise ValueError(
                u'Protocol: {0} not in currently available'
                ' protocols: {1}'.format(
                    value,
                    AVAILABLE_PROTOCOLS)
            )

    @classmethod
    def init_from_dict(cls, dict_obj):
        """Construct a model instance from a dictionary.

        This serves as a 2nd constructor

        :param dict_obj: dictionary object
        :returns o
        """
        o = cls("")
        o.domain = dict_obj.get("domain").lower().strip()
        o.protocol = dict_obj.get("protocol", "http")
        if o.protocol == 'https':
            o.certificate = dict_obj.get("certificate", None)
        return o

    def to_dict(self):
        res = super(Domain, self).to_dict()
        # cert info is a temporary property when
        # trying to create cert, so skip serialization
        if 'cert_info' in res and res['cert_info'] is not None:
            res['cert_info'] = res['cert_info'].to_dict()
        return res
