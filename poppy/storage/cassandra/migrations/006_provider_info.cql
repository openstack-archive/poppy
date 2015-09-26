CREATE TABLE providers_info (
    provider_name VARCHAR,
    info MAP<TEXT, TEXT>,
    PRIMARY KEY (provider_name)
);


--//@UNDO

DROP TABLE IF EXISTS providers_info;