"""Rackspace Cloud DNS driver"""

from poppy.dns.rackspace import driver

# Hoist classes into package namespace
Driver = driver.DNSProvider
