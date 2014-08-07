"""Fastly CDN Extension for CDN"""

from poppy.provider.fastly import driver

# Hoist classes into package namespace
Driver = driver.CDNProvider
