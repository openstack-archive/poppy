# In-memory Cassandra-ish thingy... useful for unit tests. Maybe useful for other
# stuff too? No support for SuperColumns, but that should be easy enough to add.


import bisect
import copy

from tests.unit.storage.cassandra.ttypes import Column, ColumnPath, ColumnOrSuperColumn
#from tests.unit.storage.cassandra.ttypes import NotFoundException

class SSTable(object):
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.sorted_keys = sorted(self.data.iterkeys())

    def __setitem__(self, key, value):
        if key not in self.data:
            bisect.insort(self.sorted_keys, key)
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]
        del self.sorted_keys[bisect.bisect_left(self.sorted_keys, key)]

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return self.data.__contains__(key)

    def __len__(self):
        return len(self.sorted_keys)

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def clear(self):
        self.data.clear()
        del self.sorted_keys[:]

    def copy(self):
        return self.__class__(self.data.copy())

    def key_slice(self, start, finish, count=None, reversed=False):
        start = bisect.bisect_left(self.sorted_keys, start) if start else 0
        finish = bisect.bisect_left(self.sorted_keys, finish) if finish else len(self.sorted_keys)
        keys = self.sorted_keys[start:finish]
        if reversed:
            keys.reverse()
        if count is not None:
            keys = keys[:count]
        return keys

    def slice(self, start, finish, count=None, reversed=False):
        return (self[key] for key in self.key_slice(start, finish, count, reversed))


class Cassandra(object):

    def __init__(self, keyspaces=None):
        self.database = {}
        self.keyspaces = {}
        if keyspaces is not None:
            for keyspace, column_families in keyspaces.iteritems():
                self.add_keyspace(keyspace, column_families)

    def set_keyspace(self, keyspace):
        pass
        
    def add_keyspace(self, keyspace, column_families = None):
        self.database[keyspace] = SSTable()
        if column_families:
            self.keyspaces[keyspace] = column_families
        else:
            self.keyspaces[keyspace] = {}

    def add_column_family(column_family_name):
        if key not in self.database[keyspace]:
            self.database[keyspace][key] = dict((column_family, SSTable()) for column_family in self.keyspaces[keyspace])
        self.database[keyspace][key][column_path.column_family][column_path.column] = Column(column_path.column, value, timestamp)

    def _slice_range(self, row, predicate):
        if predicate.slice_range:
            slice_range = predicate.slice_range
            columns = list(row.slice(
                start=slice_range.start,
                finish=slice_range.finish,
                count=slice_range.count,
                reversed=slice_range.reversed
            ))
        else:
            columns = [row[column_name] for column_name in predicate.column_names if column_name in row]
        return [ColumnOrSuperColumn(column=copy.deepcopy(column)) for column in columns]

    def _get(self, keyspace, key, column_path, consistency_level):
        key = self.database[keyspace].get(key)
        if key is not None:
            column_family = key[column_path.column_family] # Should raise misconfiguration exception here if KeyError.
            try:
                return column_family[column_path.column]
            except KeyError:
                pass
        raise NotFoundException()

    def get(self, keyspace, key, column_path, consistency_level):
        return copy.deepcopy(self._get(keyspace, key, column_path, consistency_level))

    def get_slice(self, keyspace, key, column_parent, predicate, consistency_level):
        key = self.database[keyspace].get(key)
        return self._slice_range(key[column_parent.column_family], predicate) if key is not None else []

    def multiget_slice(self, keyspace, keys, column_parent, predicate, consistency_level):
        return dict((key, self.get_slice(keyspace, key, column_parent, predicate, consistency_level)) for key in keys)

    def get_range_slice(self, keyspace, column_parent, predicate, start_key, finish_key, row_count, consistency_level):
        keys = self.database[keyspace].key_slice(start_key, finish_key, count=row_count)
        return self.multiget_slice(keyspace, keys, column_parent, predicate, consistency_level)

    def get_range_slices(self, keyspace, column_parent, predicate, key_range, consistency_level):
        return self.get_range_slice(keyspace, column_parent, predicate, key_range.start_key, key_range.end_key, key_range.count, consistency_level)

    def multiget_key_range(self, keyspace, column_family, key_ranges, count, consistency_level):
        keys = []
        for key_range in key_ranges:
            key_slice = self.database[keyspace].key_slice(key_range.start_key, key_range.end_key)
            keys.extend(key for key in key_slice if len(self.database[keyspace][key][column_family]))
            if len(keys) >= count:
                break
        return keys[:count]

    def insert(self, keyspace, key, column_path, value, timestamp, consistency_level):
        try:
            column = self._get(keyspace, key, column_path, consistency_level)
            if timestamp > column.timestamp:
                column.value = value
        except NotFoundException:
            if key not in self.database[keyspace]:
                self.database[keyspace][key] = dict((column_family, SSTable()) for column_family in self.keyspaces[keyspace])
            self.database[keyspace][key][column_path.column_family][column_path.column] = Column(column_path.column, value, timestamp)

    def remove(self, keyspace, key, column_path, timestamp, consistency_level):
        key = self.database[keyspace].get(key)
        if key is not None:
            column_family = key[column_path.column_family] # Should raise misconfiguration exception here if KeyError.
            if column_path.column in column_family and timestamp >= column_family[column_path.column].timestamp:
                del column_family[column_path.column]

    def batch_insert(self, keyspace, key, cfmap, consistency_level):
        for column_family, columns in cfmap.iteritems():
            for column in columns:
                self.insert(
                    keyspace,
                    key,
                    ColumnPath(column_family=column_family, column=column.column.name),
                    column.column.value,
                    column.column.timestamp,
                    consistency_level
                )

    def batch_mutate(self, keyspace, mutation_map, consistency_level):
        for key, cfmap in mutation_map.iteritems():
            for column_family, mutations in cfmap.iteritems():
                for mutation in mutations:
                    if mutation.deletion:
                        if mutation.deletion.predicate.slice_range:
                            raise Exception('Slice range on batch mutations not supported yet.')
                        for column in mutation.deletion.predicate.column_names:
                            self.remove(
                                keyspace,
                                key,
                                ColumnPath(column_family=column_family, column=column),
                                mutation.deletion.timestamp,
                                consistency_level
                            )
                    else:
                        column = mutation.column_or_supercolumn.column
                        self.insert(
                            keyspace,
                            key,
                            ColumnPath(column_family=column_family, column=column.name),
                            column.value,
                            column.timestamp,
                            consistency_level
                        )
