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

import os
import subprocess
import sys
try:
    import uwsgi
    use_uwsgi = True
except ImportError:
    use_uwsgi = False

from poppy.openstack.common import log

LOG = log.getLogger(__name__)

if use_uwsgi:
    executable = os.path.join(uwsgi.opt['virtualenv'], 'bin', 'python')
else:
    executable = sys.executable


def main(*args):
    cmd_list = [executable] + list(args[1:])
    LOG.info("Starting subprocess %s")
    subprocess.Popen(cmd_list, stdout=sys.stdout, env=os.environ.copy())
    sys.exit()

if __name__ == '__main__':
    main(*sys.argv)
