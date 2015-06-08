ALTER TABLE services ADD operator_status varchar;
ALTER TABLE archives ADD operator_status varchar;

--//@UNDO

ALTER TABLE services DROP operator_status;
ALTER TABLE archives DROP operator_status;
