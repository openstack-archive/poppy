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

import collections
import functools
import json
import uuid

try:
    import falcon
except ImportError:
    from poppy.transport.validators import fake_falcon as falcon
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


def require_accepts_json_falcon(req, resp, params=None):
    """Raises an exception if the request does not accept JSON

    Meant to be used as a `before` hook.

    :param req: request sent
    :type req: falcon.request.Request
    :param resp: response object to return
    :type resp: falcon.response.Response
    :param params: additional parameters passed to responders
    :type params: dict
    :rtype: None
    :raises: falcon.HTTPNotAcceptable
    """
    if not req.client_accepts('application/json'):
        raise falcon.HTTPNotAcceptable(
            u"""
            Endpoint only serves `application/json`; specify client-side"""
            'media type support with the "Accept" header.',
            href=u'http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html',
            href_text=u'14.1 Accept, Hypertext Transfer Protocol -- HTTP/1.1')


class DummyResponse(object):
    pass


def custom_abort_falcon(error_info=None):
    """Error_handler for with_schema

    Meant to be used with falcon transport.

    param errors: a list of validation exceptions
    """
    ret = DummyResponse()
    ret.code = 400
    if not isinstance(error_info, collections.Iterable):
        error_info = [error_info]
    details = dict(errors=[{'message': str(getattr(error, "message", error))}
                           for error in error_info])
    ret.message = json.dumps(details)
    return ret


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


def with_schema_falcon(request, schema=None):
    """Use to decorate a falcon style controller route

    :param request: A falcon request
    :param schema: a Json schema to validate against
    """
    validation_failed = False
    v_error = None
    if schema is not None:
        errors_list = []
        try:
            data = json.loads(request.body)
            errors_list = list(
                jsonschema.Draft3Validator(schema).iter_errors(data))
        except ValueError:
            validation_failed = True
            v_error = ["Invalid JSON body in request"]

        if len(errors_list) > 0:
            validation_failed = True
            v_error = errors_list

    if validation_failed:
        raise exceptions.ValidationFailed(repr(v_error))


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


def json_matches_schema_inner(request, schema=None):
    errors_list = []

    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        raise exceptions.ValidationFailed('Invalid JSON string')

    if schema is not None:
        errors_list = list(
            jsonschema.Draft3Validator(schema).iter_errors(data))

    if len(errors_list) > 0:
        details = dict(errors=[{
            'message': '-'.join([
                "[%s]" % "][".join(repr(p) for p in error.path),
                str(getattr(error, "message", error))
            ])}
            for error in errors_list])
        raise exceptions.ValidationFailed(json.dumps(details))
    else:
        return


def json_matches_schema(input_schema):
    return functools.partial(
        json_matches_schema_inner,
        schema=input_schema)


@decorators.validation_function
def is_valid_service_id(service_id):
    try:
        uuid.UUID(service_id)
    except ValueError:
        raise exceptions.ValidationFailed('Invalid service id')


@decorators.validation_function
def is_valid_flavor_id(flavor_id):
    pass


def abort_with_message(error_info):
    pecan.abort(400, detail=getattr(error_info, "message", ""),
                headers={'Content-Type': "application/json"})
