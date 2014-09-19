from tests.unit.storage.cassandra.thrift import TType
#from tests.unit.storage.cassnadra.ttypes import 

class Column(object):
  """
  Basic unit of data within a ColumnFamily.
  @param name, the name by which this column is set and retrieved.  Maximum 64KB long.
  @param value. The data associated with the name.  Maximum 2GB long, but in practice you should limit it to small numbers of MB (since Thrift must read the full value into memory to operate on it).
  @param timestamp. The timestamp is used for conflict detection/resolution when two columns with same name need to be compared.
  @param ttl. An optional, positive delay (in seconds) after which the column will be automatically deleted.

  Attributes:
   - name
   - value
   - timestamp
   - ttl
  """

  def __init__(self, name=None, value=None, timestamp=None, ttl=None,):
    self.name = name
    self.value = value
    self.timestamp = timestamp
    self.ttl = ttl

  def read(self, iprot):
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.name = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.value = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.ttl = iprot.readI32();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    oprot.writeStructBegin('Column')
    if self.name is not None:
      oprot.writeFieldBegin('name', TType.STRING, 1)
      oprot.writeString(self.name)
      oprot.writeFieldEnd()
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.STRING, 2)
      oprot.writeString(self.value)
      oprot.writeFieldEnd()
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 3)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    if self.ttl is not None:
      oprot.writeFieldBegin('ttl', TType.I32, 4)
      oprot.writeI32(self.ttl)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.name is None:
      raise TProtocol.TProtocolException(message='Required field name is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)


class ColumnPath(object):
  """
  The ColumnPath is the path to a single column in Cassandra. It might make sense to think of ColumnPath and
  ColumnParent in terms of a directory structure.

  ColumnPath is used to looking up a single column.

  @param column_family. The name of the CF of the column being looked up.
  @param super_column. The super column name.
  @param column. The column name.

  Attributes:
   - column_family
   - super_column
   - column
  """

  def __init__(self, column_family=None, super_column=None, column=None,):
    self.column_family = column_family
    self.super_column = super_column
    self.column = column

  def read(self, iprot):
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 3:
        if ftype == TType.STRING:
          self.column_family = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.super_column = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.column = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    oprot.writeStructBegin('ColumnPath')
    if self.column_family is not None:
      oprot.writeFieldBegin('column_family', TType.STRING, 3)
      oprot.writeString(self.column_family)
      oprot.writeFieldEnd()
    if self.super_column is not None:
      oprot.writeFieldBegin('super_column', TType.STRING, 4)
      oprot.writeString(self.super_column)
      oprot.writeFieldEnd()
    if self.column is not None:
      oprot.writeFieldBegin('column', TType.STRING, 5)
      oprot.writeString(self.column)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.column_family is None:
      raise TProtocol.TProtocolException(message='Required field column_family is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)


class ColumnOrSuperColumn(object):
  """
  Methods for fetching rows/records from Cassandra will return either a single instance of ColumnOrSuperColumn or a list
  of ColumnOrSuperColumns (get_slice()). If you're looking up a SuperColumn (or list of SuperColumns) then the resulting
  instances of ColumnOrSuperColumn will have the requested SuperColumn in the attribute super_column. For queries resulting
  in Columns, those values will be in the attribute column. This change was made between 0.3 and 0.4 to standardize on
  single query methods that may return either a SuperColumn or Column.

  If the query was on a counter column family, you will either get a counter_column (instead of a column) or a
  counter_super_column (instead of a super_column)

  @param column. The Column returned by get() or get_slice().
  @param super_column. The SuperColumn returned by get() or get_slice().
  @param counter_column. The Counterolumn returned by get() or get_slice().
  @param counter_super_column. The CounterSuperColumn returned by get() or get_slice().

  Attributes:
   - column
   - super_column
   - counter_column
   - counter_super_column
  """

  def __init__(self, column=None, super_column=None, counter_column=None, counter_super_column=None,):
    self.column = column
    self.super_column = super_column
    self.counter_column = counter_column
    self.counter_super_column = counter_super_column

  def read(self, iprot):
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.column = Column()
          self.column.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.super_column = SuperColumn()
          self.super_column.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.counter_column = CounterColumn()
          self.counter_column.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRUCT:
          self.counter_super_column = CounterSuperColumn()
          self.counter_super_column.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    oprot.writeStructBegin('ColumnOrSuperColumn')
    if self.column is not None:
      oprot.writeFieldBegin('column', TType.STRUCT, 1)
      self.column.write(oprot)
      oprot.writeFieldEnd()
    if self.super_column is not None:
      oprot.writeFieldBegin('super_column', TType.STRUCT, 2)
      self.super_column.write(oprot)
      oprot.writeFieldEnd()
    if self.counter_column is not None:
      oprot.writeFieldBegin('counter_column', TType.STRUCT, 3)
      self.counter_column.write(oprot)
      oprot.writeFieldEnd()
    if self.counter_super_column is not None:
      oprot.writeFieldBegin('counter_super_column', TType.STRUCT, 4)
      self.counter_super_column.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
