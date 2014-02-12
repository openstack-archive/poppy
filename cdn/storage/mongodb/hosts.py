# stevedore/example/simple.py
from storage import base


class HostController(base.HostBase):

    def list(self, project=None, marker=None,
             limit=None, detailed=False):
        print "list"

    def create(self):
        print "create"

    def delete(self):
        print "delete"
