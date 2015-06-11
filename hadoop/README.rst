Log Delivery
============

The pig script needs to be run in a hadoop cluster, after piping all the required logs from a provider with whom services are set up with.

NOTE: 
    * All the domains that need to have logs delivered need to copied into the Hadoop Cluster, under the name `domains_log.tsv`
    * The corresponding Provider URL needs to be also set

How to run a Pig Script
=======================

    $ pig -p INPUT=~/log_source -p OUTPUT=~/logs_output -p PROVIDER_URL_EXT=mycdn


Output
======

There should be directories created under OUTPUT, with each directory corresponding to a domain that had log delivered enabled, and log files underneath each of those directories pertaining to that domain.

    $ logs_output/mydomain/mydomain-0000.gz
    $ logs_output/yourdomain/yourdomain-0000.gz
