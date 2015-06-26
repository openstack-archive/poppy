#!/bin/bash


is_ready() {
    nc -z cassandra 9042
}

# wait until is ready
while ! is_ready -eq 1
do
  echo "$(date) - still trying to connect to cassandra"
  sleep 1
done
echo "$(date) - connected successfully to cassandra"

# start the app
exec /usr/local/bin/uwsgi --ini /root/uwsgi.ini