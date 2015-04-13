ALTER TABLE services ADD log_delivery varchar;

--//@UNDO

ALTER TABLE services DROP log_delivery;
