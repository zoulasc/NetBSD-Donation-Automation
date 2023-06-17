\c test_database 

DROP TABLE netbsd.donation_details;
DROP TABLE netbsd.feedbacks;

DROP SCHEMA netbsd;

\c postgres 

DROP DATABASE test_database;

DROP ROLE test_user;
