import datetime

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask_headers import headers
from flask_wtf import form

app = Flask(__name__)


@app.route('/')
def index():
    return 'Test Flask Site from 23.253.156.204'


@app.route('/hello/', strict_slashes=False)
def hello():
    return 'halo halo from 23.253.156.204'


@app.route('/hello/<user_name>/')
def hello_user(user_name):
    print(request.headers)
    return render_template('hello.html', name=user_name)


@app.route('/test/host-header/')
def test_host_header():
    print(request.headers)
    return render_template('hello.html', name=request.headers['Host'])


@app.route('/hello/<user_name>/upload/', methods=['GET', 'POST'])
def upload_file(user_name):
    if request.method == 'POST':
        form.photo.data.save('/var/www/uploads/{0}.jpg'.format(user_name))
    else:
        return render_template('gorilla.html', name=user_name)


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
    app.debug = True
    app.run(host='0.0.0.0', port=80)
