ALTER TABLE services ADD operator_status varchar;

--//@UNDO

ALTER TABLE services DROP operator_status;
