CREATE TABLE service_status (
    service_id UUID,
    project_id VARCHAR,
    status VARCHAR,
    PRIMARY KEY (service_id));


CREATE INDEX status_index on service_status (status);

--//@UNDO

DROP TABLE service_status;
DROP INDEX status_index;