"""Fastly CDN Extension for CDN"""

from cdn.provider.fastly import driver

# Hoist classes into package namespace
Driver = driver.CDNProvider
