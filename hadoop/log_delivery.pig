REGISTER /usr/lib/pig/piggybank.jar;

logs = LOAD '$INPUT/*.gz' USING PigStorage('\t') AS (date, time, ip, method, uri, status, bytes:long, time_taken, referer, user_agent, cookie, country);

log_domains = LOAD '$INPUT/domains_log.tsv' USING PigStorage('\n') AS domains;

formatted_logs = FOREACH logs GENERATE ip, '-', '-', org.apache.pig.builtin.StringConcat('[',date,':',time, ' +0000',']') , org.apache.pig.builtin.StringConcat('"', method,' ', uri,' ','HTTP/1.1', '"'), status, bytes, referer, user_agent, REGEX_EXTRACT(uri, '/([^/]*).$PROVIDER_URL_EXT(/.*)', 1) AS domain;

delivery_enabled_formamatted_logs = JOIN log_domains BY domains, formatted_logs BY domain;

STORE delivery_enabled_formamatted_logs INTO '$OUTPUT' USING org.apache.pig.piggybank.storage.MultiStorage('$OUTPUT', 10, 'gz', '\\t');
