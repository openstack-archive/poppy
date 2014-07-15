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

from stoplight.exceptions import *
from stoplight import validation_function

from pecan import request, response, redirect, abort
import falcon
import json
import jsonschema


@validation_function
def req_accepts_json_pecan(request, desired_content_type):
    # Assume the transport is pecan for now
    # for falcon the syntax should actually be:
    # request.accept('application/json')
    if request.accept('application/json'):
        raise ValidationFailed('Invalid Accept Header')


def require_accepts_json_falcon(req, resp, params):
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


def custom_abort_falcon(errors):
    """
    Error_handler for with Schema
    For pecan, you'd need a handler to internally redirect to a URI path.

    """
    ret = DummyResponse()
    ret.code = 400
    details = dict(errors=[{ 'message' : str(error.message) } for error in errors ])
    ret.message = json.dumps(details)
    return ret


def custom_abort_pecan(errors):
    """
    Error_handler for with Schema
    For pecan, you'd need a handler to internally redirect to a URI path.

    """
    # TODO(tonytan4ever): gettext support
    details = dict(errors=[{ 'message' : str(error.message) } for error in errors ])
    abort(400, detail=details, headers={'Content-Type':"application/json"})


def with_schema_falcon(request, schema=None):
    """
    Use to decorate a falcon style controller route

    :param request: A falcon request
    :param schema: a Json schema to validate against
    """
    validation_failed = False
    v_error = None
    if not schema is None:
        errors_list = []
        try:
            data = json.loads(request.body)
            errors_list = list(jsonschema.Draft3Validator(schema).iter_errors(data))
        except ValueError, e:
            validation_failed = True
            v_error = ["Invalid JSON body in request"]

        if len(errors_list) > 0:
                validation_failed = True
                v_error = errors_list
 
    if validation_failed:
        raise ValidationFailed(repr(v_error))


def with_schema_pecan(request, schema=None, handler=custom_abort_pecan, **kw):
    """
    Used to decorate a Pecan/Flask style controller form validation for 
    anything else (e.g., POST | PUT | PATCH ).

    For an HTTP POST or PUT (RFC2616 unsafe methods) request, the schema is
    used to validate the request body.

    :param schema: A JSON schema.
    :param handler: A Function (Error_handler)
    """
    def decorator(f):

        def wrapped(*args, **kwargs):
            validation_failed = False
            v_error = None
            if request.method in ('POST', 'PUT', 'PATCH') and not schema is None:
                try:
                    data = json.loads(request.body)
                    errors_list = list(jsonschema.Draft3Validator(schema).iter_errors(data))
                except ValueError, e:
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
