domain = {
    'type': 'object',
    'properties': {
        'domain': {'type': 'string',
                   'pattern': '^([a-zA-Z0-9-.]+(.com))$'}},
        'required': ['domain']
}

origin = {
    'type': 'object',
    'properties': {
        'origin': {'type': 'string',
                   'pattern': '^([a-zA-Z0-9-.]{5,1000})$'},
        'port': {'type': 'number',
                 'minumum': 0,
                 'maximum': 100000},
        'ssl': {'type': 'boolean'},
        'rules': {'type': 'array'}},
    'required': ['origin', 'port', 'ssl'],
    'additionalProperties': False,
}

cache = {'type': 'object',
         'properties': {
             'name': {'type': 'string', 'pattern': '^[a-zA-Z0-9_-]{1,64}$'},
             'ttl': {'type': 'number', 'minimum': 1, 'maximum': 36000},
             'rules': {'type': 'array'}},
         'required': ['name', 'ttl'],
         'additionalProperties': False}

links = {'type': 'object',
         'properties': {
             'href': {'type': 'string',
                      'pattern': '^/v1.0/services/[a-zA-Z0-9_-]{1,64}$'},
             'rel': {'type': 'string'}}
         }

restrictions = {'type': 'array'}

#Response Schema Definition for Create Service API
create_service = {
    'type': 'object',
    'properties': {
        'domains': {'type': 'array',
                    'items': domain,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'origins': {'type': 'array',
                    'items': origin,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'caching': {'type': 'array',
                    'items': cache,
                    'minItems': 1,
                    'maxItems': 10
                    },
        'links': {'type': 'array',
                  'items': links,
                  'minItems': 1,
                  'maxItems': 1},
        'restrictions': restrictions,
    },
    'required': ['domains', 'origins', 'caching', 'links', 'restrictions'],
    'additionalProperties': False}
