CREATE INDEX log_delivery_index on services(log_delivery);

--//@UNDO

DROP INDEX log_delivery_index;
