..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Provider Details
================

===============================      ================  ================  ================  =====================  ==========================
Header                                Poppy             Akamai            CloudFront        Fastly                 MaxCDN
===============================      ================  ================  ================  =====================  ==========================
Name of CDN site                      Service           Policy            Distribution      Service                Pull Zone
Name of Origin                        Origin            Origin            Origin            Backend                Origin
Access URL                            Custom URL        Vanity URL        CloudFront URL    Domain  URL            Custom Domain URL
Interface Format                      JSON              JSON              XML               JSON                   JSON
Python client                         None              None              boto              fastly-py,             python-maxcdn
                                                                                            fastly-python
Logs                                   -                                  S3                S3/syslog/FTP/Storm    S3/ReportsAPI/RawLogsAPI
Subaccount support                    N/A               Yes               Yes (AWS IAM)     Yes                    Yes
Propagation Time
Create                                N/A               15 mins           15 mins           100 ms                 100 ms
Update                                N/A               15 mins           15 mins           100 ms                 100 ms
Purge                                 N/A               ?                 ?                 300 ms                 100 ms
Data transfer rate                                                        1,000 Mbps
Requests per second                                                       1000
CDNs/account                                                              Default: 200      Default: 20?
RTMPs/account                                                             100
CNAMEs/service                                                            100
Origins/service                                                           25
Cache behaviors/service                                                   25
Whitelisted headers/cache                                                 10
Whitelisted cookies/cache                                                 10

Analytics                                                                 Hourly(Web)       Realtime               Realtime
Failover                                                                  AWS Route53       Yes                    ?
Loadbalancing                                                             AWS ELB           Yes                    Yes
Billing                                                                   Pay as you go     Pay as you go          Various plans available
HTTP Accelerators                                                         No Information    Varnish                Varnish
Web TTL
Minimum                                                                   0 Seconds         0 Seconds              0 Seconds
Maximum                                                                   Year: 2038        > 30 days              > 30 days
Tick                                                                      Seconds           Seconds                Seconds (Using headers)
Default                                                                   24 Hours          1 Hour                 24 Hours
Media TTL
Minimum                                                                   1 Hour
Maximum                                                                   Year: 2038        > 30 days              > 30 days
Tick                                                                      Seconds           Seconds                Seconds (Using headers)
Default                                                                   24 Hours          1 Hour                 24 Hours
===============================      ================  ================  ================  =====================  ==========================
