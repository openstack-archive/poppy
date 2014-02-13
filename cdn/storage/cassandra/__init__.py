"""MongoDB Storage Driver for Marconi"""

from cdn.storage.cassandra import driver

# Hoist classes into package namespace
StorageDriver = driver.StorageDriver
