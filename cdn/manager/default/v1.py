from cdn.manager import base

JSON_HOME = {
            "resources": {
                "rel/cdn": {
                    "href-template": "services{?marker,limit}",
                    "href-vars": {
                        "marker": "param/marker",
                        "limit": "param/limit"
                    },
                    "hints": {
                        "allow": [
                            "GET"
                        ],
                        "formats": {
                            "application/json": {}
                        }
                    }
                }
            }
        }


class DefaultV1Controller(base.V1Controller):
    def __init__(self, manager):
        super(DefaultV1Controller, self).__init__(manager)

        self.JSON_HOME = JSON_HOME

    def get(self):
        return self.JSON_HOME
