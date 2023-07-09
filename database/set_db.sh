#!/bin/bash

# Checking if psql is installed
if ! command -v psql &> /dev/null
then
    echo "PostgreSQL is not installed, exiting"
    exit
fi

# Database variables
DB_USER="donations_user"
DB_PASS="root"
DB_NAME="donations_data"
DB_FILE="db.sql"

# Checking if database already exists
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "Database $DB_NAME already exists, exiting"
    exit
fi

# Creating database and tables
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 
createdb -U $DB_USER -O $DB_USER $DB_NAME
psql -U $DB_USER -d $DB_NAME -f $DB_FILE

echo "Database $DB_NAME has been created"
