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

"""Stoplight -- an input validation framework for Python

Problem Statement:

Every good programmer should know that input validation is the first and
best step at implementing application-level security for your product.
Unvalidated user input leads to issues such as SQL injection, javascript
inject and cross-site scripting attacks, etc.

More and more applications are being written for python. Unfortunately,
not many frameworks provide for reasonable input validation techniques
and when the do, the frameworks tend further tie your application
into that framework.

For more complex projects that must supply more input validations, a
frame-work based validation framework becomes even more useless because
the validations must be done in different ways for each transport,
meaning that the chance of a programmer missing a crucial validation
is greatly increased.

A very common programming paradigm for wsgi-based applications is for
applications to expose RESTful endpoints as method members of a
controller class...."""
