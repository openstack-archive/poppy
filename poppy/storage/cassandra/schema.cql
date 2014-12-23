CREATE KEYSPACE poppy WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;
USE poppy;

CREATE TABLE services (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    flavor_id VARCHAR,
    domains LIST<TEXT>,
    origins LIST<TEXT>,
    caching_rules LIST<TEXT>,
    restrictions LIST<TEXT>,
    provider_details MAP<TEXT, TEXT>,
    PRIMARY KEY (project_id, service_id)
); 

CREATE TABLE service_names (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    PRIMARY KEY (service_name)
);

CREATE TABLE archives (
    project_id VARCHAR,
    service_id UUID,
    service_name VARCHAR,
    flavor_id VARCHAR,
    domains LIST<TEXT>,
    origins LIST<TEXT>,
    caching_rules LIST<TEXT>,
    restrictions LIST<TEXT>,
    provider_details MAP<TEXT, TEXT>,
    archived_time timestamp,
    PRIMARY KEY (project_id, service_id, archived_time)
);

CREATE TABLE flavors (
    flavor_id VARCHAR,
    providers MAP<TEXT, TEXT>,
    PRIMARY KEY (flavor_id)
);
