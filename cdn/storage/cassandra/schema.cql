CREATE KEYSPACE cdn_schema_denormalized WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;
USE cdn_schema_denormalized;

CREATE TABLE services(
  project_id VARCHAR,
  service_name VARCHAR, 
  PRIMARY KEY(project_id, service_name)
);

CREATE TABLE service_domains(
    project_id VARCHAR,
    service_name VARCHAR,
    domain_name VARCHAR,
    PRIMARY KEY (project_id, service_name, domain_name)
);

CREATE TABLE service_origins(
    project_id VARCHAR,
    service_name VARCHAR,
    origin_location VARCHAR,
    port INT,
    ssl BOOLEAN,
    rules LIST<UUID>,
    PRIMARY KEY (project_id, service_name, origin_location)
);

CREATE TABLE service_caching_rules(
    project_id VARCHAR,
    service_name VARCHAR,
    caching_name VARCHAR,
    ttl INT,
    rules LIST<UUID>,
    PRIMARY KEY (project_id, service_name, caching_name)
);

CREATE TABLE service_restrictions(
    project_id VARCHAR,
    service_name VARCHAR,
    restriction_name VARCHAR,
    rules LIST<UUID>,
    PRIMARY KEY (project_id, service_name, restriction_name)
);

CREATE TABLE service_rules(
    project_id VARCHAR,
    service_name VARCHAR,
    rule_id UUID,
    rule_name VARCHAR,
    request_uri VARCHAR,
    http_host VARCHAR,
    client_ip VARCHAR,
    http_method VARCHAR,
    PRIMARY KEY (project_id, service_name, rule_id)
);



CREATE KEYSPACE cdn_schema_one WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;
USE cdn_schema_wide;

