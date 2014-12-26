#!/usr/bin/env bash

# Setup Configs
echo "Setting Configs"
CONFIG=/etc/poppy.conf

sed -i -e "s/DNS_USERNAME/$DNS_USERNAME/"                   $CONFIG
sed -i -e "s/DNS_APIKEY/$DNS_APIKEY/"                       $CONFIG
sed -i -e "s/DNS_URL/$DNS_URL/"                             $CONFIG
sed -i -e "s/DNS_EMAIL/$DNS_EMAIL/"                         $CONFIG

sed -i -e "s/FASTLY_APIKEY/$FASTLY_APIKEY/"                 $CONFIG

sed -i -e "s/AKAM_POLICY_API_CLIENT_TOKEN/$AKAM_POLICY_API_CLIENT_TOKEN/"   $CONFIG
sed -i -e "s/AKAM_POLICY_API_CLIENT_SECRET/$AKAM_POLICY_API_CLIENT_SECRET/" $CONFIG
sed -i -e "s/AKAM_POLICY_API_ACCESS_TOKEN/$AKAM_POLICY_API_ACCESS_TOKEN/"   $CONFIG
sed -i -e "s/AKAM_POLICY_API_BASE_URL/$AKAM_POLICY_API_BASE_URL/"           $CONFIG
sed -i -e "s/AKAM_CCU_API_CLIENT_TOKEN/$AKAM_CCU_API_CLIENT_TOKEN/"         $CONFIG
sed -i -e "s/AKAM_CCU_API_CLIENT_SECRET/$AKAM_CCU_API_CLIENT_SECRET/"       $CONFIG
sed -i -e "s/AKAM_CCU_API_ACCESS_TOKEN/$AKAM_CCU_API_ACCESS_TOKEN/"         $CONFIG
sed -i -e "s/AKAM_CCU_API_BASE_URL/$AKAM_CCU_API_BASE_URL/"                 $CONFIG
sed -i -e "s/AKAM_ACCESS_URL_LINK/$AKAM_ACCESS_URL_LINK/"                   $CONFIG
sed -i -e "s/AKAM_SECURE_URL_LINK/$AKAM_SECURE_URL_LINK/"                   $CONFIG
sed -i -e "s/AKAM_HTTP_POLICY/$AKAM_HTTP_POLICY/"                           $CONFIG
sed -i -e "s/AKAM_HTTPS_POLICY/$AKAM_HTTPS_POLICY/"                         $CONFIG


/usr/local/bin/uwsgi --ini /root/uwsgi.ini
