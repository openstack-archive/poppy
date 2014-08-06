"""CDN Extension for CDN"""

from cdn.provider.mock import driver

# Hoist classes into package namespace
Driver = driver.CDNProvider
