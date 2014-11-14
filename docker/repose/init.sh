#!/usr/bin/env bash

# Setup Configs
echo "Setting Configs"
CONFIG=/etc/repose/
sed -i -e "s/KEYSTONE_ADMIN/$KEYSTONE_ADMIN/"                  $CONFIG/client-auth-n.cfg.xml
sed -i -e "s/KEYSTONE_PASSWORD/$KEYSTONE_PASSWORD/"            $CONFIG/client-auth-n.cfg.xml
sed -i -e "s/KEYSTONE_URI/$KEYSTONE_URI/"                      $CONFIG/client-auth-n.cfg.xml

sed -i -e "s/DESTINATION_HOST/$DESTINATION_HOST/"              $CONFIG/system-model.cfg.xml
sed -i -e "s/DESTINATION_PORT/$DESTINATION_PORT/"               $CONFIG/system-model.cfg.xml

echo "Starting Repose"
java -jar /usr/share/repose/repose-valve.jar
