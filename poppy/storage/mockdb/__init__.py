"""Storage Driver for CDN"""

from poppy.storage.mockdb import driver

# Hoist classes into package namespace
Driver = driver.MockDBStorageDriver
