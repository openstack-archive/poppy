# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import grammer

def parse_use_keyspace(cmd):
    #tokens = grammer.useStmt.parseString(cmd)
    return 'poppy'

def parse_select_stmt(cmd):
    tokens = grammer.selectStmt.parseString(cmd)
    print "tokens = ",        tokens
    print "tokens.columns =", tokens.columns
    print "tokens.tables =",  tokens.tables
    print "tokens.where =", tokens.where

def parse_create_keyspace(cmd):
    pass

def parse_select_statement(cmd):
    pass

def parse_insert_statement(cmd):
    pass

def parse_update_statement(cmd):
    pass

def parse_delete_command(cmd):
    pass


def parse(cmd, args):
    if re.match(grammer.CREATE_KEYSPACE_CMD, cmd):
        return 'add_keyspace', parse_create_keyspace(cmd)
    elif re.match(grammer.USE_KEYSPACE_CMD, cmd):
        return 'set_keyspace', parse_use_keyspace(cmd)
    elif re.match(grammer.SELECT_CMD, cmd):
        return 'select', parse_select_statement(cmd)
    elif re.match(grammer.INSERT_CMD, cmd):
        return 'insert', parse_insert_statement(cmd)
    elif re.match(grammer.UPDATE_CMD, cmd):
        return 'update', parse_update_statement(cmd)
    elif re.match(grammer.DELETE_CMD, cmd):
        return 'delete', parse_delete_command(cmd)
    else:
        return None, None
