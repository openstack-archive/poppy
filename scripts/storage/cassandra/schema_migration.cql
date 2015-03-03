CREATE TABLE IF NOT EXISTS schema_migrations(
    type text,
    version int,
    PRIMARY KEY(type, version))
    WITH COMMENT = 'Schema migration history'
    AND CLUSTERING ORDER BY (version DESC);

INSERT INTO schema_migrations (type, version) VALUES ('migration', 1);