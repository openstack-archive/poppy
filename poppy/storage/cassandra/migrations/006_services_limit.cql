CREATE TABLE service_limits (
    project_id VARCHAR,
    project_limit INT,
    PRIMARY KEY (project_id)
);


--//@UNDO

DROP TABLE service_limits;