CREATE TABLE service_status (
    status VARCHAR,
    project_id VARCHAR,
    service_id UUID,
    PRIMARY KEY (status, project_id, service_id)
);


--//@UNDO

DROP TABLE service_status;