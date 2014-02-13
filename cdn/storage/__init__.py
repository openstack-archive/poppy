"""Marconi Storage Drivers"""

from cdn.storage import base
from cdn.storage import errors  # NOQA

# Hoist classes into package namespace
StorageDriverBase = base.StorageDriverBase

HostBase = base.HostBase
