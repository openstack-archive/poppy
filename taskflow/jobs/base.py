# -*- coding: utf-8 -*-

#    Copyright (C) 2013 Rackspace Hosting Inc. All Rights Reserved.
#    Copyright (C) 2013 Yahoo! Inc. All Rights Reserved.
#
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

import abc
import collections
import contextlib

from oslo_utils import uuidutils
import six

from taskflow import exceptions as excp
from taskflow import states
from taskflow.types import notifier


@six.add_metaclass(abc.ABCMeta)
class Job(object):
    """A abstraction that represents a named and trackable unit of work.

    A job connects a logbook, a owner, last modified and created on dates and
    any associated state that the job has. Since it is a connector to a
    logbook, which are each associated with a set of factories that can create
    set of flows, it is the current top-level container for a piece of work
    that can be owned by an entity (typically that entity will read those
    logbooks and run any contained flows).

    Only one entity will be allowed to own and operate on the flows contained
    in a job at a given time (for the foreseeable future).

    NOTE(harlowja): It is the object that will be transferred to another
    entity on failure so that the contained flows ownership can be
    transferred to the secondary entity/owner for resumption, continuation,
    reverting...
    """

    def __init__(self, board, name,
                 uuid=None, details=None, backend=None,
                 book=None, book_data=None):
        if uuid:
            self._uuid = uuid
        else:
            self._uuid = uuidutils.generate_uuid()
        self._name = name
        if not details:
            details = {}
        self._details = details
        self._backend = backend
        self._board = board
        self._book = book
        if not book_data:
            book_data = {}
        self._book_data = book_data

    @abc.abstractproperty
    def last_modified(self):
        """The datetime the job was last modified."""

    @abc.abstractproperty
    def created_on(self):
        """The datetime the job was created on."""

    @property
    def board(self):
        """The board this job was posted on or was created from."""
        return self._board

    @abc.abstractproperty
    def state(self):
        """Access the current state of this job."""
        pass

    @property
    def book(self):
        """Logbook associated with this job.

        If no logbook is associated with this job, this property is None.
        """
        if self._book is None:
            self._book = self._load_book()
        return self._book

    @property
    def book_uuid(self):
        """UUID of logbook associated with this job.

        If no logbook is associated with this job, this property is None.
        """
        if self._book is not None:
            return self._book.uuid
        else:
            return self._book_data.get('uuid')

    @property
    def book_name(self):
        """Name of logbook associated with this job.

        If no logbook is associated with this job, this property is None.
        """
        if self._book is not None:
            return self._book.name
        else:
            return self._book_data.get('name')

    @property
    def uuid(self):
        """The uuid of this job."""
        return self._uuid

    @property
    def details(self):
        """A dictionary of any details associated with this job."""
        return self._details

    @property
    def name(self):
        """The non-uniquely identifying name of this job."""
        return self._name

    def _load_book(self):
        book_uuid = self.book_uuid
        if self._backend is not None and book_uuid is not None:
            # TODO(harlowja): we are currently limited by assuming that the
            # job posted has the same backend as this loader (to start this
            # seems to be a ok assumption, and can be adjusted in the future
            # if we determine there is a use-case for multi-backend loaders,
            # aka a registry of loaders).
            with contextlib.closing(self._backend.get_connection()) as conn:
                return conn.get_logbook(book_uuid)
        # No backend to fetch from or no uuid specified
        return None

    def __str__(self):
        """Pretty formats the job into something *more* meaningful."""
        return "%s: %s (uuid=%s, details=%s)" % (type(self).__name__,
                                                 self.name, self.uuid,
                                                 self.details)


class JobBoardIterator(six.Iterator):
    """Iterator over a jobboard that iterates over potential jobs.

    It provides the following attributes:

    * ``only_unclaimed``: boolean that indicates whether to only iterate
      over unclaimed jobs
    * ``ensure_fresh``: boolean that requests that during every fetch of a new
      set of jobs this will cause the iterator to force the backend to
      refresh (ensuring that the jobboard has the most recent job listings)
    * ``board``: the board this iterator was created from
    """

    _UNCLAIMED_JOB_STATES = (states.UNCLAIMED,)
    _JOB_STATES = (states.UNCLAIMED, states.COMPLETE, states.CLAIMED)

    def __init__(self, board, logger,
                 board_fetch_func=None, board_removal_func=None,
                 only_unclaimed=False, ensure_fresh=False):
        self._board = board
        self._logger = logger
        self._board_removal_func = board_removal_func
        self._board_fetch_func = board_fetch_func
        self._fetched = False
        self._jobs = collections.deque()
        self.only_unclaimed = only_unclaimed
        self.ensure_fresh = ensure_fresh

    @property
    def board(self):
        """The board this iterator was created from."""
        return self._board

    def __iter__(self):
        return self

    def _next_job(self):
        if self.only_unclaimed:
            allowed_states = self._UNCLAIMED_JOB_STATES
        else:
            allowed_states = self._JOB_STATES
        job = None
        while self._jobs and job is None:
            maybe_job = self._jobs.popleft()
            try:
                if maybe_job.state in allowed_states:
                    job = maybe_job
            except excp.JobFailure:
                self._logger.warn("Failed determining the state of"
                                  " job '%s'", maybe_job, exc_info=True)
            except excp.NotFound:
                if self._board_removal_func is not None:
                    self._board_removal_func(maybe_job)
        return job

    def __next__(self):
        if not self._jobs:
            if not self._fetched:
                if self._board_fetch_func is not None:
                    self._jobs.extend(
                        self._board_fetch_func(
                            ensure_fresh=self.ensure_fresh))
                self._fetched = True
        job = self._next_job()
        if job is None:
            raise StopIteration
        else:
            return job


@six.add_metaclass(abc.ABCMeta)
class JobBoard(object):
    """A place where jobs can be posted, reposted, claimed and transferred.

    There can be multiple implementations of this job board, depending on the
    desired semantics and capabilities of the underlying jobboard
    implementation.

    NOTE(harlowja): the name is meant to be an analogous to a board/posting
    system that is used in newspapers, or elsewhere to solicit jobs that
    people can interview and apply for (and then work on & complete).
    """

    def __init__(self, name, conf):
        self._name = name
        self._conf = conf

    @abc.abstractmethod
    def iterjobs(self, only_unclaimed=False, ensure_fresh=False):
        """Returns an iterator of jobs that are currently on this board.

        NOTE(harlowja): the ordering of this iteration should be by posting
        order (oldest to newest) if possible, but it is left up to the backing
        implementation to provide the order that best suits it (so don't depend
        on it always being oldest to newest).

        NOTE(harlowja): the iterator that is returned may support other
        attributes which can be used to further customize how iteration can
        be accomplished; check with the backends iterator object to determine
        what other attributes are supported.

        :param only_unclaimed: boolean that indicates whether to only iteration
            over unclaimed jobs.
        :param ensure_fresh: boolean that requests to only iterate over the
            most recent jobs available, where the definition of what is recent
            is backend specific. It is allowable that a backend may ignore this
            value if the backends internal semantics/capabilities can not
            support this argument.
        """

    @abc.abstractmethod
    def wait(self, timeout=None):
        """Waits a given amount of time for jobs to be posted.

        When jobs are found then an iterator will be returned that can be used
        to iterate over those jobs.

        NOTE(harlowja): since a jobboard can be mutated on by multiple external
        entities at the *same* time the iterator that can be returned *may*
        still be empty due to other entities removing those jobs after the
        iterator has been created (be aware of this when using it).

        :param timeout: float that indicates how long to wait for a job to
            appear (if None then waits forever).
        """

    @abc.abstractproperty
    def job_count(self):
        """Returns how many jobs are on this jobboard.

        NOTE(harlowja): this count may change as jobs appear or are removed so
        the accuracy of this count should not be used in a way that requires
        it to be exact & absolute.
        """

    @abc.abstractmethod
    def find_owner(self, job):
        """Gets the owner of the job if one exists."""

    @property
    def name(self):
        """The non-uniquely identifying name of this jobboard."""
        return self._name

    @abc.abstractmethod
    def consume(self, job, who):
        """Permanently (and atomically) removes a job from the jobboard.

        Consumption signals to the board (and any others examining the board)
        that this job has been completed by the entity that previously claimed
        that job.

        Only the entity that has claimed that job is able to consume the job.

        A job that has been consumed can not be reclaimed or reposted by
        another entity (job postings are immutable). Any entity consuming
        a unclaimed job (or a job they do not have a claim on) will cause an
        exception.

        :param job: a job on this jobboard that can be consumed (if it does
            not exist then a NotFound exception will be raised).
        :param who: string that names the entity performing the consumption,
            this must be the same name that was used for claiming this job.
        """

    @abc.abstractmethod
    def post(self, name, book=None, details=None):
        """Atomically creates and posts a job to the jobboard.

        This posting allowing others to attempt to claim that job (and
        subsequently work on that job). The contents of the provided logbook,
        details dictionary, or name (or a mix of these) must provide *enough*
        information for consumers to reference to construct and perform that
        jobs contained work (whatever it may be).

        Once a job has been posted it can only be removed by consuming that
        job (after that job is claimed). Any entity can post/propose jobs
        to the jobboard (in the future this may be restricted).

        Returns a job object representing the information that was posted.
        """

    @abc.abstractmethod
    def claim(self, job, who):
        """Atomically attempts to claim the provided job.

        If a job is claimed it is expected that the entity that claims that job
        will at sometime in the future work on that jobs contents and either
        fail at completing them (resulting in a reposting) or consume that job
        from the jobboard (signaling its completion). If claiming fails then
        a corresponding exception will be raised to signal this to the claim
        attempter.

        :param job: a job on this jobboard that can be claimed (if it does
            not exist then a NotFound exception will be raised).
        :param who: string that names the claiming entity.
        """

    @abc.abstractmethod
    def abandon(self, job, who):
        """Atomically attempts to abandon the provided job.

        This abandonment signals to others that the job may now be reclaimed.
        This would typically occur if the entity that has claimed the job has
        failed or is unable to complete the job or jobs it had previously
        claimed.

        Only the entity that has claimed that job can abandon a job. Any entity
        abandoning a unclaimed job (or a job they do not own) will cause an
        exception.

        :param job: a job on this jobboard that can be abandoned (if it does
            not exist then a NotFound exception will be raised).
        :param who: string that names the entity performing the abandoning,
            this must be the same name that was used for claiming this job.
        """

    @abc.abstractmethod
    def trash(self, job, who):
        """Trash the provided job.

        Trashing a job signals to others that the job is broken and should not
        be reclaimed. This is provided as an option for users to be able to
        remove jobs from the board externally.  The trashed job details should
        be kept around in an alternate location to be reviewed, if desired.

        Only the entity that has claimed that job can trash a job. Any entity
        trashing a unclaimed job (or a job they do not own) will cause an
        exception.

        :param job: a job on this jobboard that can be trashed (if it does
            not exist then a NotFound exception will be raised).
        :param who: string that names the entity performing the trashing,
            this must be the same name that was used for claiming this job.
        """

    @abc.abstractmethod
    def register_entity(self, entity):
        """Register an entity to the jobboard('s backend), e.g: a conductor"""

    @abc.abstractproperty
    def connected(self):
        """Returns if this jobboard is connected."""

    @abc.abstractmethod
    def connect(self):
        """Opens the connection to any backend system."""

    @abc.abstractmethod
    def close(self):
        """Close the connection to any backend system.

        Once closed the jobboard can no longer be used (unless reconnection
        occurs).
        """


# Jobboard events
POSTED = 'POSTED'  # new job is/has been posted
REMOVAL = 'REMOVAL'  # existing job is/has been removed


class NotifyingJobBoard(JobBoard):
    """A jobboard subclass that can notify others about board events.

    Implementers are expected to notify *at least* about jobs being posted
    and removed.

    NOTE(harlowja): notifications that are emitted *may* be emitted on a
    separate dedicated thread when they occur, so ensure that all callbacks
    registered are thread safe (and block for as little time as possible).
    """
    def __init__(self, name, conf):
        super(NotifyingJobBoard, self).__init__(name, conf)
        self.notifier = notifier.Notifier()


# Internal helpers for usage by board implementations...

def check_who(meth):

    @six.wraps(meth)
    def wrapper(self, job, who, *args, **kwargs):
        if not isinstance(who, six.string_types):
            raise TypeError("Job applicant must be a string type")
        if len(who) == 0:
            raise ValueError("Job applicant must be non-empty")
        return meth(self, job, who, *args, **kwargs)

    return wrapper


def format_posting(uuid, name, created_on=None, last_modified=None,
                   details=None, book=None):
    posting = {
        'uuid': uuid,
        'name': name,
    }
    if created_on is not None:
        posting['created_on'] = created_on
    if last_modified is not None:
        posting['last_modified'] = last_modified
    if details:
        posting['details'] = details
    else:
        posting['details'] = {}
    if book is not None:
        posting['book'] = {
            'name': book.name,
            'uuid': book.uuid,
        }
    return posting
