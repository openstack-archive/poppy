#!/usr/bin/env bash

IP=`hostname --ip-address`
SEEDS=`env | grep CASS[0-9]_PORT_9042_TCP_ADDR | sed 's/CASS[0-9]_PORT_9042_TCP_ADDR=//g' | sed -e :a -e N -e 's/\n/,/' -e ta`

if [ -z "$SEEDS" ]; then
SEEDS=$IP
fi

echo "Listening on: "$IP
echo "Found seeds: "$SEEDS

# Setup Cassandra
CONFIG=/etc/cassandra/
sed -i -e "s/^listen_address.*/listen_address: $IP/"            $CONFIG/cassandra.yaml
sed -i -e "s/^rpc_address.*/rpc_address: 0.0.0.0/"              $CONFIG/cassandra.yaml
sed -i -e "s/- seeds: \"127.0.0.1\"/- seeds: \"$SEEDS\"/"       $CONFIG/cassandra.yaml
sed -i -e "s/# JVM_OPTS=\"$JVM_OPTS -Djava.rmi.server.hostname=<public name>\"/ JVM_OPTS=\"$JVM_OPTS -Djava.rmi.server.hostname=$IP\"/" $CONFIG/cassandra-env.sh

# Start Cassandra
echo Starting Cassandra...
cassandra -f -p /var/run/cassandra.pid