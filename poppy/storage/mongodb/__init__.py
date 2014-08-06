"""MongoDB Storage Driver for CDN"""

from cdn.storage.mongodb import driver

# Hoist classes into package namespace
Driver = driver.MongoDBStorageDriver
