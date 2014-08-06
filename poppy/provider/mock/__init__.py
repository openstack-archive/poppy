"""CDN Extension for CDN"""

from poppy.provider.mock import driver

# Hoist classes into package namespace
Driver = driver.CDNProvider
