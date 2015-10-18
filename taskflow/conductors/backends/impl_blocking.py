# -*- coding: utf-8 -*-

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import socket

import threading

try:
    from contextlib import ExitStack  # noqa
except ImportError:
    from contextlib2 import ExitStack  # noqa

from debtcollector import removals
from oslo_utils import excutils
import six
from taskflow.conductors import base
from taskflow import exceptions as excp
from taskflow.listeners import logging as logging_listener
from taskflow import logging
from taskflow.types import entity
from taskflow.types import timing as tt
from taskflow.utils import async_utils
from taskflow.utils import iter_utils

LOG = logging.getLogger(__name__)
WAIT_TIMEOUT = 0.5
NO_CONSUME_EXCEPTIONS = tuple([
    excp.ExecutionFailure,
    excp.StorageFailure,
])


class BlockingConductor(base.Conductor):
    """A conductor that runs jobs in its own dispatching loop.

    This conductor iterates over jobs in the provided jobboard (waiting for
    the given timeout if no jobs exist) and attempts to claim them, work on
    those jobs in its local thread (blocking further work from being claimed
    and consumed) and then consume those work units after completion. This
    process will repeat until the conductor has been stopped or other critical
    error occurs.

    NOTE(harlowja): consumption occurs even if a engine fails to run due to
    a task failure. This is only skipped when an execution failure or
    a storage failure occurs which are *usually* correctable by re-running on
    a different conductor (storage failures and execution failures may be
    transient issues that can be worked around by later execution). If a job
    after completing can not be consumed or abandoned the conductor relies
    upon the jobboard capabilities to automatically abandon these jobs.
    """

    START_FINISH_EVENTS_EMITTED = tuple([
        'compilation', 'preparation',
        'validation', 'running',
    ])
    """Events will be emitted for the start and finish of each engine
       activity defined above, the actual event name that can be registered
       to subscribe to will be ``${event}_start`` and ``${event}_end`` where
       the ``${event}`` in this pseudo-variable will be one of these events.
    """

    def __init__(self, name, jobboard,
                 persistence=None, engine=None,
                 engine_options=None, wait_timeout=None):
        super(BlockingConductor, self).__init__(
            name, jobboard, persistence=persistence,
            engine=engine, engine_options=engine_options)
        if wait_timeout is None:
            wait_timeout = WAIT_TIMEOUT
        if isinstance(wait_timeout, (int, float) + six.string_types):
            self._wait_timeout = tt.Timeout(float(wait_timeout))
        elif isinstance(wait_timeout, tt.Timeout):
            self._wait_timeout = wait_timeout
        else:
            raise ValueError("Invalid timeout literal: %s" % (wait_timeout))
        self._dead = threading.Event()

    @removals.removed_kwarg('timeout', version="0.8", removal_version="2.0")
    def stop(self, timeout=None):
        """Requests the conductor to stop dispatching.

        This method can be used to request that a conductor stop its
        consumption & dispatching loop.

        The method returns immediately regardless of whether the conductor has
        been stopped.

        .. deprecated:: 0.8

            The ``timeout`` parameter is **deprecated** and is present for
            backward compatibility **only**. In order to wait for the
            conductor to gracefully shut down, :py:meth:`wait` should be used
            instead.
        """
        self._wait_timeout.interrupt()

    @property
    def dispatching(self):
        return not self._dead.is_set()

    def _listeners_from_job(self, job, engine):
        listeners = super(BlockingConductor, self)._listeners_from_job(job,
                                                                       engine)
        listeners.append(logging_listener.LoggingListener(engine, log=LOG))
        return listeners

    def _dispatch_job(self, job):
        engine = self._engine_from_job(job)
        listeners = self._listeners_from_job(job, engine)
        with ExitStack() as stack:
            for listener in listeners:
                stack.enter_context(listener)
            LOG.debug("Dispatching engine for job '%s'", job)
            consume = True
            try:
                for stage_func, event_name in [(engine.compile, 'compilation'),
                                               (engine.prepare, 'preparation'),
                                               (engine.validate, 'validation'),
                                               (engine.run, 'running')]:
                    self._notifier.notify("%s_start" % event_name, {
                        'job': job,
                        'engine': engine,
                        'conductor': self,
                    })
                    stage_func()
                    self._notifier.notify("%s_end" % event_name, {
                        'job': job,
                        'engine': engine,
                        'conductor': self,
                    })
            except excp.WrappedFailure as e:
                if all((f.check(*NO_CONSUME_EXCEPTIONS) for f in e)):
                    consume = False
                if LOG.isEnabledFor(logging.WARNING):
                    if consume:
                        LOG.warn("Job execution failed (consumption being"
                                 " skipped): %s [%s failures]", job, len(e))
                    else:
                        LOG.warn("Job execution failed (consumption"
                                 " proceeding): %s [%s failures]", job, len(e))
                    # Show the failure/s + traceback (if possible)...
                    for i, f in enumerate(e):
                        LOG.warn("%s. %s", i + 1, f.pformat(traceback=True))
            except NO_CONSUME_EXCEPTIONS:
                LOG.warn("Job execution failed (consumption being"
                         " skipped): %s", job, exc_info=True)
                consume = False
            except Exception:
                LOG.warn("Job execution failed (consumption proceeding): %s",
                         job, exc_info=True)
            else:
                LOG.info("Job completed successfully: %s", job)
            return async_utils.make_completed_future(consume)

    def _get_conductor_info(self):
        """For right now we just register the conductor name as:

        <conductor_name>@<hostname>:<process_pid>

        """
        hostname = socket.gethostname()
        pid = os.getpid()
        name = '@'.join([
            self._name, hostname+":"+str(pid)])
        # Can add a lot more information here,
        metadata = {
            "hostname": hostname,
            "pid": pid
        }

        return entity.Entity("conductor", name, metadata)

    def run(self, max_dispatches=None):
        self._dead.clear()

        # Register a conductor type entity
        self._jobboard.register_entity(self._get_conductor_info())

        total_dispatched = 0
        try:

            if max_dispatches is None:
                # NOTE(TheSriram): if max_dispatches is not set,
                # then the  conductor will run indefinitely, and not
                # stop after 'n' number of dispatches
                max_dispatches = -1

            dispatch_gen = iter_utils.iter_forever(max_dispatches)

            while True:
                if self._wait_timeout.is_stopped():
                    break
                local_dispatched = 0
                for job in self._jobboard.iterjobs():
                    if self._wait_timeout.is_stopped():
                        break
                    LOG.debug("Trying to claim job: %s", job)
                    try:
                        self._jobboard.claim(job, self._name)
                    except (excp.UnclaimableJob, excp.NotFound):
                        LOG.debug("Job already claimed or consumed: %s", job)
                        continue
                    consume = False
                    try:
                        f = self._dispatch_job(job)
                    except KeyboardInterrupt:
                        with excutils.save_and_reraise_exception():
                            LOG.warn("Job dispatching interrupted: %s", job)
                    except Exception:
                        LOG.warn("Job dispatching failed: %s", job,
                                 exc_info=True)
                    else:

                        local_dispatched += 1
                        consume = f.result()
                    try:
                        if consume:
                            self._jobboard.consume(job, self._name)
                        else:
                            self._jobboard.abandon(job, self._name)
                    except (excp.JobFailure, excp.NotFound):
                        if consume:
                            LOG.warn("Failed job consumption: %s", job,
                                     exc_info=True)
                        else:
                            LOG.warn("Failed job abandonment: %s", job,
                                     exc_info=True)

                    total_dispatched = next(dispatch_gen)

                if local_dispatched == 0 and \
                        not self._wait_timeout.is_stopped():
                    self._wait_timeout.wait()

        except StopIteration:
            if max_dispatches >= 0 and total_dispatched >= max_dispatches:
                LOG.info("Maximum dispatch limit of %s reached",
                         max_dispatches)
        finally:
            self._dead.set()

    def wait(self, timeout=None):
        """Waits for the conductor to gracefully exit.

        This method waits for the conductor to gracefully exit. An optional
        timeout can be provided, which will cause the method to return
        within the specified timeout. If the timeout is reached, the returned
        value will be False.

        :param timeout: Maximum number of seconds that the :meth:`wait` method
                        should block for.
        """
        return self._dead.wait(timeout)
