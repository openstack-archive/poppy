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

import jsonschema
import pecan
import stoplight


def pecan_getter(parm):
    """getter."""
    pecan_module = __import__('pecan', globals(), locals(), ['request'])
    return getattr(pecan_module, 'request')


def req_accepts_json(request, desired_content_type='application/json'):
    if not request.accept(desired_content_type):
        raise stoplight.exceptions.ValidationFailed('Invalid Accept Header')


def custom_abort(errors_info):
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


def with_schema(request, schema=None, handler=custom_abort,
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
        raise stoplight.exceptions.ValidationFailed('Invalid JSON string')

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

        raise stoplight.exceptions.ValidationFailed(json.dumps(details))
    else:
        return


def json_matches_schema(input_schema):
    return functools.partial(
        json_matches_schema_inner,
        schema=input_schema)


def abort_with_message(error_info):
    pecan.abort(400, detail=getattr(error_info, "message", ""),
                headers={'Content-Type': "application/json"})
