"""Storage Driver for CDN"""

from cdn.storage.mockdb import driver

# Hoist classes into package namespace
StorageDriver = driver.StorageDriver
