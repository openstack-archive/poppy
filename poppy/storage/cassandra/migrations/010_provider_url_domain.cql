CREATE TABLE provider_url_domain (
    provider_url VARCHAR,
    domain_name VARCHAR,
    PRIMARY KEY (provider_url, domain_name));


--//@UNDO

DROP TABLE provider_url_domain;