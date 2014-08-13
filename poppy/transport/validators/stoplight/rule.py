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

import collections

ValidationRule = collections.namedtuple('ValidationRule',
                                        'vfunc errfunc getter'
                                        )


def Rule(vfunc, on_error, getter=None):
    """Constructs a single validation rule.

    A rule effectively is saying "I want to validation this input using
    this function and if validation fails I want this (on_error)
    to happen.

    :param vfunc: The function used to validate this param
    :param on_error: The function to call when an error is detected
    :param value_src: The source from which the value can be
        This function should take a value as a field name
        as a single param.
    """
    return ValidationRule(vfunc=vfunc, errfunc=on_error, getter=getter)
