#!/bin/bash


is_ready() {
    nc -z cassandra 9042
}

# wait until cassandra is ready
while ! is_ready -eq 1
do
  echo "$(date) - still trying to connect to cassandra"
  sleep 1
done
echo "$(date) - connected successfully to cassandra"


# start the poppy-workers
exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &

exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &

exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &
exec poppy-worker > /dev/null 2>&1 &

# start the poppy-server (via uwsgi)
exec /usr/local/bin/uwsgi --ini /root/uwsgi.ini