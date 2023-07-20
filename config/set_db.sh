#!/bin/bash

set -e
PREFIX=donations
DB_USER="${PREFIX}_user"
DB_PASS="test@123"
DB_NAME="${PREFIX}_data"

# Database variables
if [ $(uname) = "NetBSD" ]; then
   POSTGRES=pgsql
else
   POSTGRES=postgres
fi

PROG=$(basename "$0")

substitute() {
    sed -e s/@PREFIX@/${PREFIX}/g -e s/@PASSWORD@/${DB_PASS}/g $@
}

usage() {
    echo "Usage: $PROG -d|c" 1>&2
    exit 1
}

# Checking if psql is installed
if ! command -v psql &> /dev/null
then
    echo "${PROG}: PostgreSQL is not installed, exiting" 1>&2
    exit 1
fi

no=true
while getopts dc arg; do
    case $arg in
    c)	no=false;;
    d)
	set +e
	psql -U ${POSTGRES} -d postgres -c "DROP DATABASE ${DB_NAME}"
	psql -U ${POSTGRES} -d postgres -c "DROP ROLE ${DB_USER}"
	exit 0
	;;
    *)	usage;;
    esac
done

if $no; then
    usage
fi
	
substitute __init__.py.in > __init__.py

# Checking if database already exists
if psql -U ${POSTGRES} -lqt | cut -d \| -f 1 | grep -qw ${DB_NAME}; then
    echo "$PROG: Database $DB_NAME already exists, exiting" 1>&2
    exit 1
fi

# Creating database and tables
psql -U ${POSTGRES} -d postgres -c \
    "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';" 
createdb -U ${POSTGRES} -O ${DB_USER} ${DB_NAME}
substitute db.sql | psql -U ${DB_USER} -d ${DB_NAME} -f -

echo "Database $DB_NAME has been created"
