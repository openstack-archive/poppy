#!/bin/bash

case $# in
    0)
        HOST=localhost
        PORT=8888;;
    1)
        HOST=$1
        PORT=8888;;
    2)
        HOST=$1
        PORT=$2;;
esac

curl --include \
     --request POST \
     --header "Content-Type: application/json" \
     --header "X-Project-ID: 123456" \
     --data-binary '{
    "id" : "cdn",
    "limits": [{
        "origins": {
            "min": 1,
            "max": 5
        },
        "domains" : {
            "min": 1,
            "max": 5
        },
        "caching": {
            "min": 3600,
            "max": 604800,
            "incr": 300
        }
    }],
    "providers" : [
        {
            "provider" : "akamai",
            "links": [
                {
                    "href": "http://www.akamai.com",
                    "rel": "provider_url"
                }
            ]
        }
    ]
}' "http://$HOST:$PORT/v1.0/flavors"
