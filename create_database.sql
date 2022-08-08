CREATE USER test_user WITH PASSWORD 'test@123';
ALTER USER test_user WITH SUPERUSER;


CREATE DATABASE test_database
  WITH OWNER = test_user
       ENCODING = 'UTF8';


\c test_database


CREATE SCHEMA "netbsd"
  AUTHORIZATION test_user;


CREATE TABLE netbsd.donation_details
(
  confirmation_no character varying NOT NULL,
  contributor character varying,
  currency character varying,
  quantity integer,
  email character varying NOT NULL,
  vendor character varying NOT NULL,
  datetime character varying,
  amount character varying NOT NULL,
  CONSTRAINT payment_id PRIMARY KEY (confirmation_no)
);
ALTER TABLE netbsd.donation_details
  OWNER TO test_user;
