"""Zaqar Queue driver"""

from poppy.queue.zaqar import driver

# Hoist classes into package namespace
Driver = driver.QueueProvider
