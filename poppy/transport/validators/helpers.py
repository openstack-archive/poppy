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

import functools
import json
import re
try:
    set
except NameError:  # noqa  pragma: no cover
    from sets import Set as set  # noqa  pragma: no cover
import uuid

import jsonschema
import pecan

from poppy.common import util
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import exceptions


def req_accepts_json_pecan(request, desired_content_type='application/json'):
    # Assume the transport is pecan for now
    # for falcon the syntax should actually be:
    # request.accept('application/json')
    if not request.accept(desired_content_type):
        raise exceptions.ValidationFailed('Invalid Accept Header')


def custom_abort_pecan(errors_info):
    """Error_handler for with_schema

    Meant to be used with pecan transport.

    param errors: a list of validation exceptions
    """
    # TODO(tonytan4ever): gettext support
    details = dict(errors=[{'message': str(getattr(error, "message", error))}
                           for error in errors_info])
    pecan.abort(
        400,
        detail=details,
        headers={
            'Content-Type': "application/json"})


def with_schema_pecan(request, schema=None, handler=custom_abort_pecan,
                      **kwargs):
    """Decorate a Pecan/Flask style controller form validation.

    For an HTTP POST or PUT (RFC2616 unsafe methods) request, the schema is
    used to validate the request body.

    :param schema: A JSON schema.
    :param handler: A Function (Error_handler)
    """
    def decorator(f):

        def wrapped(*args, **kwargs):
            validation_failed = False
            v_error = None
            errors_list = []
            if request.method in ('POST', 'PUT', 'PATCH') and (
                schema is not None
            ):
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    errors_list = list(
                        jsonschema.Draft3Validator(schema).iter_errors(data))
                except ValueError:
                    validation_failed = True
                    v_error = ["Invalid JSON body in request"]

            if len(errors_list) > 0:
                validation_failed = True
                v_error = errors_list

            if not validation_failed:
                return f(*args, **kwargs)
            else:
                return handler(v_error)

        return wrapped

    return decorator


def json_matches_service_schema(input_schema):
    return functools.partial(
        json_matches_service_schema_inner,
        schema=input_schema)


def json_matches_service_schema_inner(request, schema=None):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        raise exceptions.ValidationFailed('Invalid JSON string')

    is_valid_service_configuration(data, schema)


def json_matches_flavor_schema(input_schema):
    return functools.partial(
        json_matches_flavor_schema_inner,
        schema=input_schema)


def json_matches_flavor_schema_inner(request, schema=None):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        raise exceptions.ValidationFailed('Invalid JSON string')

    is_valid_flavor_configuration(data, schema)


def is_valid_shared_ssl_domain_name(domain_name):
    shared_ssl_domain_regex = '^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]?$'
    return re.match(shared_ssl_domain_regex, domain_name)


def is_valid_domain_name(domain_name):
    # only allow ascii
    domain_regex = ('^((?=[a-z0-9-]{1,63}\.)[a-z0-9]+'
                    '(-[a-z0-9]+)*\.)+[a-z]{2,63}$')
    # allow Punycode
    # domain_regex = ('^((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+'
    #                 '(-[a-z0-9]+)*\.)+[a-z]{2,63}$')
    return re.match(domain_regex, domain_name)


def is_valid_domain(domain):
    domain_name = domain.get('domain')
    if (domain.get('protocol') == 'https' and
            domain['certificate'] == u'shared'):
        return is_valid_shared_ssl_domain_name(domain_name)
    else:
        return is_valid_domain_name(domain_name)


def is_valid_ip_address(ip_address):
    ipv4_regex = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    return re.match(ipv4_regex, ip_address)


def is_valid_origin(origin):
    return (is_valid_domain_name(origin.get('origin')) or
            is_valid_ip_address(origin.get('origin')))


def is_valid_service_configuration(service, schema):
    if schema is not None:
        errors_list = list(
            jsonschema.Draft3Validator(schema).iter_errors(service))

    if len(errors_list) > 0:
        details = dict(errors=[{
            'message': '-'.join([
                "[%s]" % "][".join(repr(p) for p in error.path),
                str(getattr(error, "message", error))
            ])}
            for error in errors_list])
        raise exceptions.ValidationFailed(json.dumps(details))

    # Schema structure is valid.  Check the functional rules.

    # 1. origins and origin rules must be unique
    if 'origins' in service:
        origin_rules = []
        origins = []
        for origin in service['origins']:
            origin_ssl = 'https' if origin.get('ssl') else 'http'
            origin_value = u"{0}://{1}".format(origin_ssl,
                                               origin.get('origin'))
            if origin_value in origins:
                raise exceptions.ValidationFailed(
                    'Origins must be unique')
            else:
                origins.append(origin_value)

            if 'rules' in origin:
                for rule in origin['rules']:
                    request_url = rule['request_url']
                    if request_url in origin_rules:
                        raise exceptions.ValidationFailed(
                            'Origins - the request_url must be unique')
                    else:
                        origin_rules.append(request_url)

    # 2. caching rules must be unique
    if 'caching' in service:
        caching_rules = []
        for caching in service['caching']:
            if 'rules' in caching:
                for rule in caching['rules']:
                    request_url = rule['request_url']
                    if request_url in caching_rules:
                        raise exceptions.ValidationFailed(
                            'Caching Rules - the request_url must be unique')
                    else:
                        caching_rules.append(request_url)

    # 3. domains must be unique
    if 'domains' in service:
        domains = []
        for domain in service['domains']:
            domain_value = u"{0}://{1}".format(
                domain.get('protocol', 'http'), domain.get('domain'))
            if domain_value in domains:
                raise exceptions.ValidationFailed(
                    'Domains must be unique')
            else:
                domains.append(domain_value)

    # 4. referrer restriction paths must be unique
    if 'restrictions' in service:
        restriction_paths = []
        for restriction in service['restrictions']:
            if 'rules' in restriction:
                for rule in restriction['rules']:
                    if 'referrer' in rule:
                        request_url = rule.get('request_url', '/*')
                        if request_url in restriction_paths:
                            raise exceptions.ValidationFailed(
                                'Referrer - the request_url must be unique')
                        else:
                            restriction_paths.append(request_url)

    # 5. domains protocols must be of the same type, and domains protocols must
    # match the description (ssl/port) of the origin
    cdn_protocol = None
    if 'domains' in service:
        for domain in service['domains']:
            domain_protocol = domain.get('protocol', 'http')
            if cdn_protocol is None:
                cdn_protocol = domain_protocol
            else:
                if cdn_protocol != domain_protocol:
                    raise exceptions.ValidationFailed(
                        'Domains must in the same protocol')

    protocol_port_mapping = {
        'http': 80,
        'https': 443
    }

    # 6. origin port must match the domain's protocol
    if 'origins' in service:
        for origin in service['origins']:
            origin_port = origin.get('port', 80)
            if protocol_port_mapping[cdn_protocol] != origin_port:
                raise exceptions.ValidationFailed(
                    'Domain port does not match origin port')

    # 7. domains must be valid
    if 'domains' in service:
        for domain in service['domains']:
            if not is_valid_domain(domain):
                raise exceptions.ValidationFailed(
                    u'Domain {0} is not valid'.format(domain.get('domain')))

    # 8. origins and domains cannot be the same
    if 'origins' in service and 'domains' in service:
        origins = set()
        for origin in service['origins']:
            origin_name = origin.get('origin').lower().strip()
            origins.add(origin_name)

        domains = set()
        for domain in service['domains']:
            domain_name = domain.get('domain').lower().strip()
            domains.add(domain_name)

        if origins.intersection(domains):
            raise exceptions.ValidationFailed(
                u'Domains and origins cannot be same: {0}'.format(origin))

    # 9. origins must be valid
    if 'origins' in service:
        for origin in service['origins']:
            if not is_valid_origin(origin):
                raise exceptions.ValidationFailed(
                    u'Origin {0} is not valid'.format(origin.get('origin')))

    # 10. Hostheadervalue must be valid
    if 'origins' in service:
        for origin in service['origins']:
            if 'hostheadervalue' in origin:
                hostheadervalue = origin.get('hostheadervalue')
                if hostheadervalue is not None:
                    if not is_valid_domain_name(hostheadervalue):
                        raise exceptions.ValidationFailed(
                            u'HostHeaderValue {0} is not valid'.format(
                                hostheadervalue))

    # 11. Need to validate restriction correctness here
    # Cannot allow one restriction type to have both
    # "blacklist" and "whitelist" restriciton type
    whitelist_restriction_entities = [
    ]
    blacklist_restriction_entities = [
    ]
    if 'restrictions' in service:
        for restriction in service['restrictions']:
            if restriction.get('type', 'whitelist') == 'blacklist':
                for rule in restriction['rules']:
                    entity = None
                    for key in rule:
                        if key != 'name':
                            entity = key
                        else:
                            continue
                    blacklist_restriction_entities.append(entity)
            elif restriction.get('type', 'whitelist') == 'whitelist':
                for rule in restriction['rules']:
                    entity = None
                    for key in rule:
                        if key != 'name':
                            entity = key
                        else:
                            continue
                        if key in blacklist_restriction_entities:
                            raise exceptions.ValidationFailed(
                                'Cannot blacklist and whitelsit [%s]'
                                ' at the same time' % key)
                    whitelist_restriction_entities.append(entity)

    return


@decorators.validation_function
def is_valid_service_id(service_id):
    try:
        uuid.UUID(service_id)
    except ValueError:
        raise exceptions.ValidationFailed('Invalid service id')


def is_valid_flavor_configuration(flavor, schema):
    if schema is not None:
        errors_list = list(
            jsonschema.Draft3Validator(schema).iter_errors(flavor))

    if len(errors_list) > 0:
        details = dict(errors=[{
            'message': '-'.join([
                "[%s]" % "][".join(repr(p) for p in error.path),
                str(getattr(error, "message", error))
            ])}
            for error in errors_list])
        raise exceptions.ValidationFailed(json.dumps(details))

    return


@decorators.validation_function
def is_valid_flavor_id(flavor_id):
    pass


def abort_with_message(error_info):
    pecan.abort(400, detail=util.help_escape(
                getattr(error_info, "message", "")),
                headers={'Content-Type': "application/json"})


class DummyResponse(object):
    pass
