ALTER TABLE services ADD log_delivery boolean;

--//@UNDO

ALTER TABLE services DROP log_delivery;
