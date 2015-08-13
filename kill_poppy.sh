ps -ef | grep [p]oppy- | awk -F ' ' '{print$2}' | xargs kill -9

# remove existing containers
docker kill compose_cassandra_1
docker kill compose_zookeeper_1
docker kill compose_mimic_1
docker rm compose_cassandra_1
docker rm compose_zookeeper_1
docker rm compose_mimic_1