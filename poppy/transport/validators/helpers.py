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
import uuid

import jsonschema
import pecan

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
            origin_value = u"{0}://{1}".format(origin_ssl, origin.get('origin'))
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
    pecan.abort(400, detail=getattr(error_info, "message", ""),
                headers={'Content-Type': "application/json"})


class DummyResponse(object):
    pass
