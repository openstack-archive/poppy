import falcon


class HostsResource:
    def on_get(self, req, resp):
        """Handles GET requests
        """
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = [
            {
                'hostname': 'www.mywebsite.com',
                'description': 'My Sample Website'
            },
            {
                'hostname': 'www.myotherwebsite.com',
                'description': 'My Other Website'
            }
        ]
