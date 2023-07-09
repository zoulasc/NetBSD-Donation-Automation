DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_roles
      WHERE  rolname = 'donations_user') THEN

      CREATE ROLE donations_user LOGIN PASSWORD 'test@123';
   END IF;
END
$$;

CREATE DATABASE donations_data
    WITH
    OWNER = donations_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE SCHEMA IF NOT EXISTS donations
    AUTHORIZATION donations_user;

GRANT ALL ON SCHEMA donations TO donations_user;

CREATE TABLE IF NOT EXISTS donations.information
(
    confirmation_no integer NOT NULL,
    contributor character varying COLLATE pg_catalog."default",
    currency character varying COLLATE pg_catalog."default",
    quantity integer,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    vendor character varying COLLATE pg_catalog."default",
    datetime integer,
    amount character varying COLLATE pg_catalog."default",
    uuid character varying COLLATE pg_catalog."default",
    CONSTRAINT feedback_id PRIMARY KEY (confirmation_no)
);

ALTER TABLE IF EXISTS donations.information
    OWNER to donations_user;

GRANT ALL ON TABLE donations.information TO donations_user;

CREATE TABLE IF NOT EXISTS donations.interaction
(
    confirmation_no integer NOT NULL,
    answer1 boolean NOT NULL,
    name character varying COLLATE pg_catalog."default",
    answer2 boolean NOT NULL,
    email character varying COLLATE pg_catalog."default",
    answer3 boolean NOT NULL,
    notification_email character varying COLLATE pg_catalog."default",
    CONSTRAINT payment_id PRIMARY KEY (confirmation_no)
);

ALTER TABLE IF EXISTS donations.interaction
    OWNER to donations_user;

GRANT ALL ON TABLE donations.interaction TO donations_user;

CREATE TABLE IF NOT EXISTS donations.deferred_email
(
    confirmation_no integer NOT NULL,
    CONSTRAINT deferred_email_id PRIMARY KEY (confirmation_no)
);

ALTER TABLE IF EXISTS donations.deferred_email
    OWNER to donations_user;

GRANT ALL ON TABLE donations.deferred_email TO donations_user;
