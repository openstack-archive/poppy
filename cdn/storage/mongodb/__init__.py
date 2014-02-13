"""MongoDB Storage Driver for Marconi"""

from cdn.storage.mongodb import driver

# Hoist classes into package namespace
StorageDriver = driver.StorageDriver
