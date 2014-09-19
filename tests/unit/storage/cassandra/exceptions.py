import sys


class TException(Exception):
  """Base class for all thrift exceptions."""

  # BaseException.message is deprecated in Python v[2.6,3.0)
  if (2, 6, 0) <= sys.version_info < (3, 0):
    def _get_message(self):
      return self._message

    def _set_message(self, message):
      self._message = message
    message = property(_get_message, _set_message)

  def __init__(self, message=None):
    Exception.__init__(self, message)
    self.message = message


class NotFoundException(TException):
  """
  A specific column was requested that does not exist.
  """

  def read(self, iprot):
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    oprot.writeStructBegin('NotFoundException')
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return

  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)


class ReconnectionPolicy(object):
    """
    This class and its subclasses govern how frequently an attempt is made
    to reconnect to nodes that are marked as dead.

    If custom behavior is needed, this class may be subclassed.
    """

    def new_schedule(self):
        """
        This should return a finite or infinite iterable of delays (each as a
        floating point number of seconds) inbetween each failed reconnection
        attempt.  Note that if the iterable is finite, reconnection attempts
        will cease once the iterable is exhausted.
        """
        raise NotImplementedError()

class ExponentialReconnectionPolicy(ReconnectionPolicy):
    """
    A :class:`.ReconnectionPolicy` subclass which exponentially increases
    the length of the delay inbetween each reconnection attempt up to
    a set maximum delay.
    """

    def __init__(self, base_delay, max_delay):
        """
        `base_delay` and `max_delay` should be in floating point units of
        seconds.
        """
        if base_delay < 0 or max_delay < 0:
            raise ValueError("Delays may not be negative")

        if max_delay < base_delay:
            raise ValueError("Max delay must be greater than base delay")

        self.base_delay = base_delay
        self.max_delay = max_delay

    def new_schedule(self):
        return (min(self.base_delay * (2 ** i), self.max_delay) for i in range(64))

class RetryPolicy(object):
    """
    A policy that describes whether to retry, rethrow, or ignore timeout
    and unavailable failures.

    To specify a default retry policy, set the
    :attr:`.Cluster.default_retry_policy` attribute to an instance of this
    class or one of its subclasses.

    To specify a retry policy per query, set the :attr:`.Statement.retry_policy`
    attribute to an instance of this class or one of its subclasses.

    If custom behavior is needed for retrying certain operations,
    this class may be subclassed.
    """

    RETRY = 0
    """
    This should be returned from the below methods if the operation
    should be retried on the same connection.
    """

    RETHROW = 1
    """
    This should be returned from the below methods if the failure
    should be propagated and no more retries attempted.
    """

    IGNORE = 2
    """
    This should be returned from the below methods if the failure
    should be ignored but no more retries should be attempted.
    """

    def on_read_timeout(self, query, consistency, required_responses,
                        received_responses, data_retrieved, retry_num):
        """
        This is called when a read operation times out from the coordinator's
        perspective (i.e. a replica did not respond to the coordinator in time).
        It should return a tuple with two items: one of the class enums (such
        as :attr:`.RETRY`) and a :class:`.ConsistencyLevel` to retry the
        operation at or :const:`None` to keep the same consistency level.

        `query` is the :class:`.Statement` that timed out.

        `consistency` is the :class:`.ConsistencyLevel` that the operation was
        attempted at.

        The `required_responses` and `received_responses` parameters describe
        how many replicas needed to respond to meet the requested consistency
        level and how many actually did respond before the coordinator timed
        out the request. `data_retrieved` is a boolean indicating whether
        any of those responses contained data (as opposed to just a digest).

        `retry_num` counts how many times the operation has been retried, so
        the first time this method is called, `retry_num` will be 0.

        By default, operations will be retried at most once, and only if
        a sufficient number of replicas responded (with data digests).
        """
        if retry_num != 0:
            return (self.RETHROW, None)
        elif received_responses >= required_responses and not data_retrieved:
            return (self.RETRY, consistency)
        else:
            return (self.RETHROW, None)

    def on_write_timeout(self, query, consistency, write_type,
                         required_responses, received_responses, retry_num):
        """
        This is called when a write operation times out from the coordinator's
        perspective (i.e. a replica did not respond to the coordinator in time).

        `query` is the :class:`.Statement` that timed out.

        `consistency` is the :class:`.ConsistencyLevel` that the operation was
        attempted at.

        `write_type` is one of the :class:`.WriteType` enums describing the
        type of write operation.

        The `required_responses` and `received_responses` parameters describe
        how many replicas needed to acknowledge the write to meet the requested
        consistency level and how many replicas actually did acknowledge the
        write before the coordinator timed out the request.

        `retry_num` counts how many times the operation has been retried, so
        the first time this method is called, `retry_num` will be 0.

        By default, failed write operations will retried at most once, and
        they will only be retried if the `write_type` was
        :attr:`~.WriteType.BATCH_LOG`.
        """
        if retry_num != 0:
            return (self.RETHROW, None)
        elif write_type == WriteType.BATCH_LOG:
            return (self.RETRY, consistency)
        else:
            return (self.RETHROW, None)

    def on_unavailable(self, query, consistency, required_replicas, alive_replicas, retry_num):
        """
        This is called when the coordinator node determines that a read or
        write operation cannot be successful because the number of live
        replicas are too low to meet the requested :class:`.ConsistencyLevel`.
        This means that the read or write operation was never forwared to
        any replicas.

        `query` is the :class:`.Statement` that failed.

        `consistency` is the :class:`.ConsistencyLevel` that the operation was
        attempted at.

        `required_replicas` is the number of replicas that would have needed to
        acknowledge the operation to meet the requested consistency level.
        `alive_replicas` is the number of replicas that the coordinator
        considered alive at the time of the request.

        `retry_num` counts how many times the operation has been retried, so
        the first time this method is called, `retry_num` will be 0.

        By default, no retries will be attempted and the error will be re-raised.
        """
        return (self.RETHROW, None)
