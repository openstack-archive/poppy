"""Openstack Designate driver"""

from poppy.dns.designate import driver

# Hoist classes into package namespace
Driver = driver.DNSProvider
