"""MongoDB Storage Driver for CDN"""

from poppy.storage.mongodb import driver

# Hoist classes into package namespace
Driver = driver.MongoDBStorageDriver
