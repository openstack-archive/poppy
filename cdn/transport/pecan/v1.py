from hosts import HostsController
from pecan import expose
from pecan.rest import RestController


class HomeController(RestController):

    hosts = HostsController()

    @expose('json')
    def get_all(self):
        '''return the HOME document for the API
        '''
        return dict(
            version='1.0'
        )
