#!/bin/bash

/usr/local/bin/pip install -e /home/poppy/.
exec /usr/local/bin/uwsgi --ini /root/uwsgi.ini
