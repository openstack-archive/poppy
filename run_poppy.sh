#!/bin/bash
pip install docker-compose

# remove existing containers
docker kill compose_cassandra_1
docker kill compose_zookeeper_1
docker rm compose_cassandra_1
docker rm compose_zookeeper_1

# start new containers
docker-compose -f docker/compose/dependencies.yml up -d 

is_ready() {
    nc -z dockerhost 9042
}

# wait until cassandra is ready
while ! is_ready -eq 1
do
  echo "still trying to connect to cassandra"
  sleep 1
done
echo "connected successfully to cassandra"


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