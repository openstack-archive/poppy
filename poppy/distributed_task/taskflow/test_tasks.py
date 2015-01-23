
import logging
import time
import sys

from taskflow import task

logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)

LOG = logging.getLogger('Test Tasks')
LOG.setLevel(logging.DEBUG)


class HelloWorldTask(task.Task):
    default_provides = "hi_happened"

    def execute(self):
        LOG.info('hello world')
        return time.time()


class GoodbyeWorldTask(task.Task):
    default_provides = "goodbye_happened"

    def execute(self, hi_happened):
        LOG.info('goodbye world (hi said on %s)', hi_happened)
        return time.time()
