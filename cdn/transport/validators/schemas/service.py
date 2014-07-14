from cdn.transport.validators.schema_base import SchemaBase

class ServiceSchema(SchemaBase):
    """
    JSON Schmema validation for /service
    """
    schema = {
        'service': {
            'PUT':{
                'type' : 'object',
                'properties' : {
                    "domains" : {
                       'type':'array',
                       'items' : {
                          'type' : "object",
                          "properties": {
                                "domain" : { "type" : "string",
                                 'pattern' :  "^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})"
                                              "|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\."
                                              "([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$"
                                }
                          }
                        },
                       'required' : True,
                       "minItems" : 1
                    },
                    "origins" : {
                       'type':'array',
                       'items' : {
                          'type' : "object",
                          "properties": {
                                "origin": {"type": "string", "required": True},
                                "port": { "type": "integer",
                                          "enum" : [80, 443] },
                                "ssl": {"type": "boolean" }
                          },
                        },
                       'required' : True,
                       "minItems" : 1
                    },
                    "caching" : {
                       'type':'array',
                       'items' : {
                          'type' : "object",
                          "properties": {
                                "name": {"type": "string", "required": True},
                                "ttl": { "type": "integer", "required": True},
                                "rules": {
                                  "type": "array",
                                  'items' : {
                                    'type' : "object",
                                    "properties": {
                                      'name' : {'type' : 'string'},
                                      'request_url' : {'type' : 'string'}
                                    }
                                  },
                                }
                          },
                        },
                    },
                }
            },
            'PATCH':{
            }
        },


    }