from cdn.transport.validators.helpers import with_schema_falcon, with_schema_pecan, custom_abort_falcon
from cdn.transport.validators.schemas import service

from cdn.transport.validators.stoplight import Rule, validate, validation_function
from cdn.transport.validators.stoplight.exceptions import ValidationFailed

from pecan import expose, configuration, make_app, set_config, request
from webtest.app import AppError

import json
from unittest import TestCase

import functools
import os

os.environ['PECAN_CONFIG'] = './config.py'
from pecan.testing import load_test_app


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


class DummyFalconEndpoint(object):
    #falcon style endpoint
    @validate(
        request=Rule(request_fit_schema, lambda: abort(404)),
        response=Rule(is_response(), lambda: abort(404))
    )
    def get_falcon_style(self, request, response):
        return "Hello, World!"


class DummyPecanEndpoint(object):
    
    @expose()
    @with_schema_pecan(request, schema=testing_schema)
    def index(self):
        return "Hello, World!"



class TestFalconStyleValidationFunctions(TestCase):
    def test_with_schema_falcon(self):
        self.assertEquals(with_schema_falcon(fake_request_good, schema=testing_schema), None)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            with_schema_falcon(fake_request_bad_missing_domain, schema=testing_schema)
        with self.assertRaisesRegexp(ValidationFailed, "Invalid JSON body in request"):
            with_schema_falcon(fake_request_bad_invalid_json_body, schema=testing_schema)

    def test_partial_with_schema(self):
        self.assertEquals(request_fit_schema(fake_request_good), None)
        with self.assertRaisesRegexp(ValidationFailed, "domain"):
            request_fit_schema(fake_request_bad_missing_domain)
        with self.assertRaisesRegexp(ValidationFailed, "Invalid JSON body in request"):
            request_fit_schema(fake_request_bad_invalid_json_body)


class TestValidationDecoratorsFalcon(TestCase):

    def setUp(self):
        self.ep = DummyFalconEndpoint()

    def test_falcon_eps(self):
        class DummyResponse(object):
            pass

        response = DummyResponse()

        global error_count

        # Try to call with good inputs
        oldcount = error_count
        ret = self.ep.get_falcon_style(fake_request_good, response)
        self.assertEqual(oldcount, error_count)
        self.assertEqual(ret, "Hello, World!", "testing not passed on endpoint: get_falcon_style without error")

        # Try to call with bad inputs
        oldcount = error_count
        ret2 = self.ep.get_falcon_style(fake_request_bad_missing_domain, response)
        self.assertEqual(oldcount+1, error_count)
        


class PecanEndPointFunctionalTest(TestCase):
     """
     A Simple PecanFunctionalTest base class that sets up a 
     Pecan endpoint (endpoint class: DummyPecanEndpoint)
     """
 
     def setUp(self):
         self.app = load_test_app(os.path.join(os.path.dirname(__file__),
            'config.py'
         ))
 
     def tearDown(self):
         set_config({}, overwrite=True)


class TestValidationDecoratorsPecan(PecanEPFunctionalTest):
    
    def test_pecan_endpoint_put(self):
        resp = self.app.put('/', params=fake_request_good.body,
                             headers={"Content-Type":"application/json"})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body, "Hello, World!")
        with self.assertRaisesRegexp(AppError, "400 Bad Request"):
            self.app.put('/', params=fake_request_bad_missing_domain.body,
                             headers={"Content-Type":"application/json"})
        #assert resp.status_int == 400
