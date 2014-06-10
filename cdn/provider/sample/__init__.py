"""CDN Extension for CDN"""

from cdn.provider.sample import driver

# Hoist classes into package namespace
CDNProvider = driver.CDNProvider
