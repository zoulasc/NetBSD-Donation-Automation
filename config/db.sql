
CREATE SCHEMA IF NOT EXISTS @PREFIX@
    AUTHORIZATION @PREFIX@_user;

GRANT ALL ON SCHEMA @PREFIX@ TO @PREFIX@_user;

CREATE TABLE IF NOT EXISTS @PREFIX@.information
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

ALTER TABLE IF EXISTS @PREFIX@.information
    OWNER to @PREFIX@_user;

GRANT ALL ON TABLE @PREFIX@.information TO @PREFIX@_user;

CREATE TABLE IF NOT EXISTS @PREFIX@.interaction
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

ALTER TABLE IF EXISTS @PREFIX@.interaction
    OWNER to @PREFIX@_user;

GRANT ALL ON TABLE @PREFIX@.interaction TO @PREFIX@_user;

CREATE TABLE IF NOT EXISTS @PREFIX@.deferred_email
(
    confirmation_no integer NOT NULL,
    CONSTRAINT deferred_email_id PRIMARY KEY (confirmation_no)
);

ALTER TABLE IF EXISTS @PREFIX@.deferred_email
    OWNER to @PREFIX@_user;

GRANT ALL ON TABLE @PREFIX@.deferred_email TO @PREFIX@_user;
