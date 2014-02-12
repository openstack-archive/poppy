import abc
import six


@six.add_metaclass(abc.ABCMeta)
class HostBase(object):
    """This class is responsible for managing hostnames.
    Hostname operations include CRUD, etc.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def list(self, project=None, marker=None,
             limit=None, detailed=False):
        """Base method for listing hostnames.

        :param project: Project id
        :param marker: The last host name
        :param limit: (Default 10, configurable) Max number
            hostnames to return.
        :param detailed: Whether metadata is included

        :returns: An iterator giving a sequence of hostnames
            and the marker of the next page.
        """
        raise NotImplementedError
