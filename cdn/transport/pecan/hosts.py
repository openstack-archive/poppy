from pecan import expose, response
from pecan.rest import RestController


class HostsController(RestController):

    @expose('json')
    def get_all(self):
        '''return the list of hostnames
        '''
        return dict(
            hostname='www.sample.com'
        )

    @expose('json')
    def get(self, id):
        '''return the configuration of the hostname
        '''
        return dict(
            hostname=id,
            description='My Sample Website'
        )

    @expose('json')
    def put(self, id):
        '''add the hostname
        '''

        response.status = 201
        return dict(
            hostname=id,
            description='My Sample Website'
        )

    @expose('json')
    def delete(self, id):
        '''delete the hostname
        '''
        response.status = 204
        return None
