CREATE KEYSPACE poppy WITH REPLICATION = { 'class' : 'SimpleStrategy' , 'replication_factor' :  1}  ;
USE poppy;

CREATE TABLE services (
    project_id VARCHAR,
    service_name VARCHAR,
    domains LIST<TEXT>,
    origins LIST<TEXT>,
    caching_rules LIST<TEXT>,
    restrictions LIST<TEXT>,
    PRIMARY KEY (project_id, service_name)
); 
