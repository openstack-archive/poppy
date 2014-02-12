from pecan import expose
from v1 import HomeController


class RootController(object):

    v1 = HomeController()

    @expose('json')
    def notfound(self):
        '''return the generic 404 response
        '''
        return dict(status=404, message="Not Found")
