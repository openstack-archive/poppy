# Copyright (c) 2015 Rackspace, Inc.
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

import datetime
import requests
import sys
import time


def main(args):
    if len(args) != 4:
        print("usage: python check_headers.py [domain] [run_time] [sleep]")
        print("example : python check_headers.py http://www.mysite.com 300 5")
        sys.exit(2)

    url = args[1]
    loop = int(args[2])
    sleep_time = int(args[3])

    print ("requesting " + url)

    for x in range(0, loop / sleep_time):
        response = requests.get(url, headers={'PRAGMA': 'akamai-x-cache-on'})

        if 'X-Cache' in response.headers:
            print (str(datetime.datetime.now()) +
                   " - Akamai Response: " + str(response.headers['X-Cache']))
        else:
            print ("Not served through Akamai")

        time.sleep(sleep_time)


if __name__ == '__main__':
    main(sys.argv)
