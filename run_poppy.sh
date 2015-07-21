#!/bin/bash
pip install docker-compose

# remove any running processes
./kill_poppy.sh

# remove existing containers
docker kill compose_cassandra_1
docker kill compose_zookeeper_1
docker rm compose_cassandra_1
docker rm compose_zookeeper_1

# start new containers
docker-compose -f docker/compose/dependencies.yml up -d 

is_cassandra_ready() {
    nc -z dockerhost 9042
}

is_zookeeper_ready() {
    nc -z dockerhost 2181
}

# wait until cassandra is ready
while ! is_cassandra_ready -eq 1
do
  echo "still trying to connect to cassandra"
  sleep 1
done
echo "connected successfully to cassandra"


# wait until zookeeper is ready
while ! is_zookeeper_ready -eq 1
do
  echo "still trying to connect to zookeeper"
  sleep 1
done
echo "connected successfully to zookeeper"

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

# start the poppy-server
exec poppy-server > /dev/null 2>&1 &

echo "Poppy Server and Workers Started"