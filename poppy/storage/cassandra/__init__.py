"""Cassandra Storage Driver for CDN"""

from poppy.storage.cassandra import driver

# Hoist classes into package namespace
Driver = driver.CassandraStorageDriver
