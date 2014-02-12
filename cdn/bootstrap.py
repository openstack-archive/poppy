from __future__ import print_function
from stevedore import driver


class Bootstrap(object):
    """Defines the CDN bootstrapper.

    The bootstrap loads up drivers per a given configuration, and
    manages their lifetimes.
    """

    def __init__(self, conf):
        self.conf = conf

    def storage(self):
        print((u'Loading storage driver'))

        # create the driver manager to load the appropriate drivers
        storage_type = 'cdn.storage'

        # TODO(amitgandhinz): load this from config
        storage_name = 'mongodb'

        args = [self.conf]

        try:
            mgr = driver.DriverManager(namespace=storage_type,
                                       name=storage_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            print(exc)

    def transport(self):
        # create the driver manager to load the appropriate drivers
        transport_type = 'cdn.transport'

        # TODO(amitgandhinz): load this from config
        transport_name = 'falcon'

        args = [self.conf]

        print((u'Loading transport driver: %s'), transport_name)

        try:
            mgr = driver.DriverManager(namespace=transport_type,
                                       name=transport_name,
                                       invoke_on_load=True,
                                       invoke_args=args)
            return mgr.driver
        except RuntimeError as exc:
            print(exc)

    def run(self):
        self.transport.listen()
