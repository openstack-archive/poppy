from cdn.transport.validators.helpers import with_schema_falcon, with_schema_pecan, custom_abort_falcon
from cdn.transport.validators.schemas import service

from cdn.transport.validators.stoplight import Rule, validate, validation_function
from cdn.transport.validators.stoplight.exceptions import ValidationFailed
from pecan import expose

import json
from unittest import TestCase

import functools


error_count = 0


def abort(code):
    global error_count
    error_count = error_count + 1


class DummyRequest(object):
    def __init__(self):
        self.headers = dict(header1='headervalue1')
        self.method = "PUT"
        self.body = json.dumps({
            "domains": [
                { "domain": "www.mywebsite.com" },
                { "domain": "blog.mywebsite.com" },
            ],
            "origins": [
                {
                    "origin": "mywebsite.com",
                    "port": 80,
                    "ssl": False
                },
                {
                    "origin": "mywebsite.com",
                }
            ],
            "caching": [
                { "name" : "default", "ttl" : 3600 },
                { "name" : "home", 
                  "ttl" : 17200, 
                  "rules" : [
                        { "name" : "index", "request_url" : "/index.htm" }
                    ] 
                },
                { "name" : "images",
                  "ttl" : 12800, 
                }
            ]
        })


fake_request_good = DummyRequest()
fake_request_bad_missing_domain = DummyRequest()
fake_request_bad_missing_domain.body = json.dumps({
            "origins": [
                {
                    "origin": "mywebsite.com",
                    "port": 80,
                    "ssl": False
                }
            ],
            "caching": [
                { "name" : "default", "ttl" : 3600 },
                { "name" : "home", 
                  "ttl" : 17200, 
                  "rules" : [
                        { "name" : "index", "request_url" : "/index.htm" }
                    ] 
                },
                { "name" : "images",
                  "ttl" : 12800, 
                  "rules" : [
                        { "name" : "images", "request_url" : "*.png" }
                    ] 
                }
            ]
        })
fake_request_bad_invalid_json_body = DummyRequest()
fake_request_bad_invalid_json_body.body = "{"


@validation_function
def is_response(candidate):
    pass

testing_schema = service.ServiceSchema.get_schema("service", "PUT")

request_fit_schema = functools.partial(with_schema_falcon, schema=testing_schema)

class DummyEndpoint(object):
    #falcon style endpoint
    @validate(
        request=Rule(request_fit_schema, lambda: abort(404)),
        response=Rule(is_response(), lambda: abort(404))
    )
    def get_falcon_style(self, request, response):
        return "Hello World"

    #pecan style endpoint without error
    @expose()
    @with_schema_pecan(fake_request_good, schema=testing_schema, handler=custom_abort_falcon)
    def get_pecan_style(self):
        return "Hello World"

    #pecan style endpoint
    @expose()
    @with_schema_pecan(fake_request_bad_missing_domain, schema=testing_schema, handler=custom_abort_falcon)
    def get_pecan_style_error(self):
        return "Hello World"


class TestFalconStyleValidationFunctions(TestCase):
    def test_with_schema_falcon(self):
        with_schema_falcon(fake_request_good, schema=testing_schema)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            with_schema_falcon(fake_request_bad_missing_domain, schema=testing_schema)
        with self.assertRaisesRegexp(ValidationFailed, "Invalid JSON body in request"):
            with_schema_falcon(fake_request_bad_invalid_json_body, schema=testing_schema)

    def test_partial_with_schema_2(self):
        request_fit_schema(fake_request_good)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            request_fit_schema(fake_request_bad_missing_domain)
        with self.assertRaisesRegexp(ValidationFailed, "Invalid JSON body in request"):
            request_fit_schema(fake_request_bad_invalid_json_body)


class TestValidationDecorators(TestCase):

    def setUp(self):
        self.ep = DummyEndpoint()

    def test_pecan_eps(self):
        ret = self.ep.get_pecan_style()
        self.assertEqual(ret, "Hello World", "testing not passed on endpoint: get_pecan_style without error")
        ret2 = self.ep.get_pecan_style_error()
        self.assertEqual(ret2.code, 400,  "testing not passed on endpoint: get_pecan_style_error with error")
        self.assertEqual(json.loads(ret2.message)['errors'][0]['message'], 
                """'domains' is a required property""",  "testing not passed on endpoint: get_pecan_style_error with error")

    def test_falcon_eps(self):
        class DummyResponse(object):
            pass

        response = DummyResponse()

        global error_count

        # Try to call with good inputs
        oldcount = error_count
        ret = self.ep.get_falcon_style(fake_request_good, response)
        self.assertEqual(oldcount, error_count)
        self.assertEqual(ret, "Hello World", "testing not passed on endpoint: get_falcon_style without error")

        # Try to call with bad inputs
        oldcount = error_count
        ret2 = self.ep.get_falcon_style(fake_request_bad_missing_domain, response)
        self.assertEqual(oldcount+1, error_count)