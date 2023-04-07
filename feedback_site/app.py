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
PREPARE getfeed (text) AS
SELECT * FROM netbsd.feedbacks f WHERE f.confirmation_no = $1;
EXECUTE getfeed('{0}');

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
    identifier = cur.fetchall()
   
    cur.close()
    conn.close()
    if not identifier:
        return render_template('valid.html',fid=fid,femail=femail)
    return render_template('invalid.html',identifier=identifier)


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
