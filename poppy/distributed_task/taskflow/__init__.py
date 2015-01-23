"""MongoDB Storage Driver for CDN"""

from poppy.distributed_task.taskflow import driver

# Hoist classes into package namespace
Driver = driver.TaskFlowDistributedTaskDriver
