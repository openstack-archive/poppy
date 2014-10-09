"""DNS Default driver"""

from poppy.dns.default import driver

# Hoist classes into package namespace
Driver = driver.DNSProvider
