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
from sys import argv

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask Site served from {0}'.format(request.headers['Host'])


@app.route('/test/host-header/', strict_slashes=False)
def test_host_header():
    return render_template('hello.html', name=request.headers['Host'])


@app.route('/test/camera.jpg', strict_slashes=False)
def test_jpg():
    response = make_response(render_template('jpg.html', name='jpg'))
    return response


@app.route('/test/text.txt', strict_slashes=False)
def test_txt():
    response = app.send_static_file('pg2600.txt')
    return response


@app.route('/test/line.zip', strict_slashes=False)
def test_zip():
    response = app.send_static_file('lm2k11.zip')
    return response


@app.route('/test/cache-control/cache-control.jpg', strict_slashes=False)
def test_cache_control():
    response = make_response(render_template('cache-control.html',
                                             name='cache-control'))
    response.headers['Cache-Control'] = 'public, max-age=10'
    return response


@app.route('/test/expires/expires.jpg', strict_slashes=False)
def test_expires():
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(0, 20)
    response_expires = make_response('Expires test')
    response_expires.headers['Expires'] = expiry_time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT")
    return response_expires


@app.route('/test/expires-cache-control/expires-cache-control.jpg',
           strict_slashes=False)
def test_expires_and_cache_control():
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(0, 20)
    response = make_response('Expires & Cache Control - test')
    response.headers['Expires'] = expiry_time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT")
    response.headers['Cache-Control'] = 'public, max-age=10'
    return response


if __name__ == '__main__':
    if len(argv) > 1:
        port = int(argv[1])
    else:
        port = 80

    app.debug = True
    app.run(host='0.0.0.0', port=port)
