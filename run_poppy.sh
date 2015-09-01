#!/bin/bash
DAEMONIZED=false
WORKERS=6

for i in "$@"
do
  case $i in
      -d|--daemonized)
      DAEMONIZED=true
      shift # past argument=value
      ;;

      -w=*|--workers=*)
      WORKERS="${i#*=}"
      shift # past argument=value
      ;;

      -?|--help)
      echo "USAGE: ./run_poppy.sh -d -w=10"
      echo "-d | --daemonized : run in daemonized mode"
      echo "-w | --workers : the number of poppy-worker processes to spawn (defaults to 6)"
      exit

      shift
      ;;

      *)
      echo "Invalid Options"
      echo "Run ./run_poppy.sh --help for valid parameters."
      exit
              # unknown option
      ;;
  esac
done

pip install docker-compose


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
COUNTER=0
while [ $COUNTER -lt $WORKERS ]; do
  exec poppy-worker > /dev/null 2>&1 &
  echo "poppy-worker spawned."
  let COUNTER=COUNTER+1 
done


# start the poppy-server
if $DAEMONIZED; then
  exec poppy-server > /dev/null 2>&1 &
  echo "poppy-server spawned."
else
  exec poppy-server
fi



echo "Poppy Server and Workers Started"