class TType:
  STOP   = 0
  VOID   = 1
  BOOL   = 2
  BYTE   = 3
  I08    = 3
  DOUBLE = 4
  I16    = 6
  I32    = 8
  I64    = 10
  STRING = 11
  UTF7   = 11
  STRUCT = 12
  MAP    = 13
  SET    = 14
  LIST   = 15
  UTF8   = 16
  UTF16  = 17

  _VALUES_TO_NAMES = ('STOP',
                      'VOID',
                      'BOOL',
                      'BYTE',
                      'DOUBLE',
                      None,
                      'I16',
                      None,
                      'I32',
                      None,
                     'I64',
                     'STRING',
                     'STRUCT',
                     'MAP',
                     'SET',
                     'LIST',
                     'UTF8',
                     'UTF16')
