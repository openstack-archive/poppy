CREATE TABLE cert_status (
    domain_name VARCHAR,
    status VARCHAR,
    PRIMARY KEY (domain_name));


CREATE INDEX cert_status_index on cert_status (status);

--//@UNDO

DROP TABLE cert_status;
DROP INDEX cert_status_index;