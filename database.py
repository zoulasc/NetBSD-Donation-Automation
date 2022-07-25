import psycopg2

#establishing the connection
connection = psycopg2.connect(
   database="test_database", user='test_user', password='test@123', host='127.0.0.1', port= '5432'
)

#Setting auto commit false
connection.autocommit = False

#Creating a cursor object using the cursor() method
cursor = connection.cursor()

# Preparing SQL queries to INSERT a record into the database.
cursor.execute('''INSERT INTO netbsd.paypal_donation_details(confirmation_no, contributor, amount, currency, quantity, email, donation_date)
        VALUES ('05156965ED4410053', 'Josef Burger', 10.00, 'U.S. Dollars', 1, 'bolo@bolo.com', 'datetime.datetime(2022, 3, 25, 8, 9, 50, tzinfo=tzoffset(None, -25200))')''')
cursor.execute('''INSERT INTO netbsd.stripe_donation_details(payment_id, contributor_email, amount)
        VALUES ('ch_3KmQM12y9v89cZ3U1QEHNEbO', 'wadeamesbury@gmail.com', 10.00)''')

# Commit changes in the database
connection.commit()
print("Records inserted")

#Closing the connection
connection.close()
