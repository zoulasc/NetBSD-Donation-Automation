import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

def get_db_connection() -> psycopg2.extensions.connection:
    """establishing connection with database"""
    conn = psycopg2.connect(
        database="test_database",
        user="test_user",
        password="test@123",
        host="127.0.0.1",
        port="5432",
    )
    return conn



SQL1 ="""
PREPARE check_donation_and_feedback (text, text) AS
WITH match AS (
  SELECT d.email, d.confirmation_no
  FROM netbsd.donation_details d
  WHERE d.email = $1 AND d.confirmation_no = $2
), feedback_exists AS (
  SELECT 1
  FROM netbsd.feedbacks f
  JOIN match ON f.confirmation_no = match.confirmation_no
)
SELECT EXISTS (SELECT 1 FROM match) AS donation_exists, EXISTS (SELECT 1 FROM feedback_exists) AS feedback_recorded;

EXECUTE check_donation_and_feedback('{1}', '{0}');


"""


SQL2 = """
PREPARE SQL (text, bool, text, bool, text, bool, text) AS
INSERT INTO netbsd.feedbacks VALUES($1, $2, $3, $4, $5, $6, $7);
EXECUTE SQL('{0}','{1}','{2}','{3}','{4}','{5}','{6}');
"""


@app.route('/')
def index() -> str:
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate() -> str:
    fid=request.form['feed']
    femail=request.form['email']
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(SQL1.format(fid,femail))
    databasequeries = cur.fetchall()
    app.logger.info('--log: {0}'.format(databasequeries))

    cur.close()
    conn.close()

    #checks for if donation exists
    if not databasequeries[0][0]:
        app.logger.info('--LOG: DONATION NOT FOUND')
        return render_template('nodonation.html')

    #checls for if feedback already exists
    if databasequeries[0][1]:
        app.logger.info('--LOG: FEEDBACK ALREADY RECORDED')
        return render_template('invalid.html',identifier=fid)
    
    return render_template('valid.html',fid=fid,femail=femail)

    """
    if not identifier:
        return render_template('valid.html',fid=fid,femail=femail)
    return render_template('invalid.html',identifier=identifier)"""


@app.route('/store/<string:fid>', methods=['POST'])
def store(fid: str) -> str:
    answer1=request.form["answer1"]
    name=request.form["name"]
    if not name:
        name="Anonymous"
    answer2=request.form["answer2"]
    email=request.form["email"]
    if not email:
        email="Anonymous";
    answer3=request.form["answer3"]
    notification_email=request.form["notification_email"]
    if not notification_email:
        notification_email="Anonymous";
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(SQL2.format(
            fid,
            answer1,
            name,
            answer2,
            email,
            answer3,
            notification_email
            )
        )
    cur.close()
    conn.commit()
    conn.close()
    return render_template('thank_you.html', name=name)
