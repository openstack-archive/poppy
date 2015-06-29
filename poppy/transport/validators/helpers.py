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


def is_root_domain(domain):
    # generic country code based top level domain
    generic_cc_tld = r'''([^.]+\.(ac|biz|co|com|edu|gov|id|int|ltd|me|mil|mod|
        my|name|net|nhs|nic|nom|or|org|plc|sch|web)\.(ac|ad|ae|af|ag|ai|al|am|
        an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|
        bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cw|cx|
        cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gd|
        ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|
        ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|
        kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|
        mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|
        om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|
        sc|sd|se|sg|sh|si|sk|sl|sm|sn|so|sr|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|
        tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|
        vn|vu|wf|ws|ye|yt|za|zm|zw))$'''
    # edge cases for country code based top level domain
    australia_tld = r'''([^.]+\.(act|asn|com|csiro|edu|gov|id|net|nsw|nt|org|oz|
        qld|sa|tas|vic|wa)\.au)$'''
    austria_tld = r'''([^.]+\.(ac|co|gv|or|priv)\.at)$'''
    france_tld = r'''([^.]+\.(aeroport|avocat|avoues|cci|chambagri|
        chirurgiens-dentistes|experts-comptables|geometre-expert|greta|
        huissier-justice|medecin|notaires|pharmacien|port|veterinaire)\.fr)$'''
    hungary_tld = r'''([^.]+\.(co|2000|erotika|jogasz|sex|video|info|agrar|film|
        konyvelo|shop|org|bolt|forum|lakas|suli|priv|casino|games|media|szex|
        sport|city|hotel|news|tozsde|tm|erotica|ingatlan|reklam|utazas)\
        .hu)$'''
    russia_tld = r'''([^.]+\.(ac|com|edu|int|net|org|pp|gov|mil|test|adygeya|
        bashkiria|ulan-ude|buryatia|dagestan|nalchik|kalmykia|kchr|ptz|karelia|
        komi|mari-el|joshkar-ola|mari|mordovia|yakutia|vladikavkaz|kazan|
        tatarstan|tuva|udmurtia|izhevsk|udm|khakassia|grozny|chuvashia|altai|
        kuban|krasnoyarsk|marine|vladivostok|stavropol|stv|khabarovsk|khv|amur|
        arkhangelsk|astrakhan|belgorod|bryansk|vladimir|volgograd|tsaritsyn|
        vologda|voronezh|vrn|cbg|ivanovo|irkutsk|koenig|kaluga|kamchatka|
        kemerovo|kirov|vyatka|kostroma|kurgan|kursk|lipetsk|magadan|mosreg|
        murmansk|nnov|nov|nsk|novosibirsk|omsk|orenburg|oryol|penza|perm|pskov|
        rnd|ryazan|samara|saratov|sakhalin|yuzhno-sakhalinsk|yekaterinburg|
        e-burg|smolensk|tambov|tver|tomsk|tsk|tom|tula|tyumen|simbirsk|
        chelyabinsk|chel|chita|yaroslavl|msk|spb|bir|jar|palana|dudinka|surgut|
        chukotka|yamal|amursk|baikal|cmw|fareast|jamal|kms|k-uralsk|kustanai|
        kuzbass|magnitka|mytis|nakhodka|nkz|norilsk|snz|oskol|pyatigorsk|
        rubtsovsk|syzran|vdonskzgrad)\.ru)$'''
    south_africa_tld = r'''([^.]+\.(ac|gov|law|mil|net|nom|school)\.za)$'''
    spain_tld = r'''([^.]+\.(gob|nom|org)\.es)$'''
    turkey_tld = r'''([^.]+\.(av|bbs|bel|biz|com|dr|edu|gen|gov|info|k12|kep|
        name|net|org|pol|tel|tsk|tv|web)\.tr)$'''
    uk_tld = r'''([^.]+\.(ac|co|gov|ltd|me|mod|net|nhs|org|plc|police|sch)
        \.uk)$'''
    usa_tld = r'''([^.]+\.(al|ak|az|ar|as|ca|co|ct|de|dc|fl|ga|gu|hi|id|il|in|
        ia|ks|ky|la|me|md|ma|mi|mn|mp|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|
        or|pa|pr|ri|sc|sd|tn|tx|um|ut|vt|va|vi|wa|wv|wi|wy)\.us)$'''

    # root level cc_tld have only 3 segments
    cc_tld_regex = r'''^[^.]+\.[^.]+\.[^.]+\.[^.]$'''

    # root level international level domains have only 2 segments
    intl_tld_regex = r'''^[^.]+\.[^.]$'''

    domain_name = domain.get('domain')

    cc_tld = (re.search(generic_cc_tld, domain_name) or
              re.search(generic_cc_tld, domain_name) or
              re.search(australia_tld, domain_name) or
              re.search(austria_tld, domain_name) or
              re.search(france_tld, domain_name) or
              re.search(hungary_tld, domain_name) or
              re.search(russia_tld, domain_name) or
              re.search(south_africa_tld, domain_name) or
              re.search(spain_tld, domain_name) or
              re.search(turkey_tld, domain_name) or
              re.search(uk_tld, domain_name) or
              re.search(usa_tld, domain_name))

    # if the domain is a root level ccTLD, it should have only three segments
    # if it is a root level international TLD, it should have only two segments
    if cc_tld:
        return re.match(cc_tld_regex, domain_name)
    else:
        return re.match(intl_tld_regex, domain_name)


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

    # 10. domains must not be root domains
    if 'domains' in service:
        for domain in service['domains']:
            if is_root_domain(domain):
                raise exceptions.ValidationFailed(
                    u'Root domain {0} is not a valid domain'.format(
                        domain.get('domain')))

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
