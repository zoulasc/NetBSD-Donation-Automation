"""code to insert data in database"""

# pylint: disable=import-error

import psycopg2
from psycopg2.extensions import AsIs
import sys
import ast

with open(sys.argv[1], 'r') as details:
    detail_list=[]
    for line in details:
        detail_list.append(line.rstrip())

# establishing the connection
connection = psycopg2.connect(
    database="test_database",
    user="test_user",
    password="test@123",
    host="127.0.0.1",
    port="5432",
)

# Setting auto commit false
connection.autocommit = False

# Creating a cursor object using the cursor() method
cursor = connection.cursor()

# Preparing SQL queries to INSERT a record into the database.
for detail in detail_list:
    detail=ast.literal_eval(detail)
    columns = detail.keys()
    values = [detail[column] for column in columns]
    SQL = "INSERT INTO netbsd.donation_details (%s) VALUES %s"

    # inserting records in the database
    cursor.execute(SQL, (AsIs(",".join(columns)), tuple(values)))

# Commit changes in the database
connection.commit()
print("Records inserted in the database")

# Closing the connection
connection.close()
