CREATE USER test_user WITH PASSWORD 'test@123';
ALTER USER test_user WITH SUPERUSER;


CREATE DATABASE test_database
  WITH TEMPLATE = template0
       OWNER = test_user
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
  CONSTRAINT feedback_id PRIMARY KEY (confirmation_no)
);
ALTER TABLE netbsd.donation_details
  OWNER TO test_user;


CREATE TABLE netbsd.feedbacks
(
  confirmation_no character varying NOT NULL,
  answer1 boolean NOT NULL,
  name character varying,
  answer2 boolean NOT NULL,
  email character varying,
  answer3 boolean NOT NULL,
  notificationi_email character varying,
  CONSTRAINT payment_id PRIMARY KEY (confirmation_no)
);
ALTER TABLE netbsd.feedbacks
  OWNER TO test_user;
