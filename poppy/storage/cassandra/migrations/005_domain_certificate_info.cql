CREATE TABLE certificate_info (
    project_id VARCHAR,
    flavor_id VARCHAR,
    cert_type VARCHAR,
    domain_name VARCHAR,
    cert_domain VARCHAR,
    cert_details MAP<TEXT, TEXT>,
    PRIMARY KEY (project_id, flavor_id, cert_type, domain_name)
);

--//@UNDO

DROP TABLE IF EXISTS certificate_info;