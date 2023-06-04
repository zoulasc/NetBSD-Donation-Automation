import psycopg2
from flask import Flask, render_template, request
import uuid
import ssl
import os
import smtplib
from configparser import ConfigParser

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


def sendmail(mail: str):
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")
    smtp_server = config["smtp"]["server"]
    port_no = config["smtp"]["port"]
    sender_email = config["email"]["sender"]
    sender_password = os.environ[
        "PASSWORD"
    ]  # SET ENV VARIABLE OR USE CONFIG.INI config["email"]["password"]
    receiver_email = config["email"]["receiver"]
    # sending all mails to the address defined in config.ini for test purposes
    # receiver_email = data["email"] if not "Unknown"
    ack_text = config["msg"]["text"]
    msg = ack_text
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_server, int(port_no), context=context)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg)
    server.quit()
    app.logger.info("\n--LOG: Mail Sent\n")


SQL1 = """
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

EXECUTE check_donation_and_feedback('{mail}', '{fid}');


"""


SQL2 = """
PREPARE SQL (text, bool, text, bool, text, bool, text) AS
INSERT INTO netbsd.feedbacks VALUES($1, $2, $3, $4, $5, $6, $7);
EXECUTE SQL('{fid}','{ans1}','{name}','{ans2}','{mail1}','{ans3}','{mail2}');
"""

SQL3 = """
PREPARE checkbymail (uuid) AS
SELECT confirmation_no, email FROM netbsd.donation_details WHERE access_token = $1;
EXECUTE checkbymail('{token}');
"""

SQL4 = """
PREPARE check_feedback (text) AS
SELECT EXISTS(SELECT 1 FROM netbsd.feedbacks WHERE confirmation_no = $1);
EXECUTE check_feedback('{fid}');
"""


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate() -> str:
    fid = request.form["feed"]
    femail = request.form["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(SQL1.format(fid=fid, mail=femail))
    databasequeries = cur.fetchall()
    app.logger.info("\n--log: {0}\n".format(databasequeries))

    cur.close()
    conn.close()

    # checks for if donation exists
    if not databasequeries[0][0]:
        app.logger.info("\n--LOG: DONATION NOT FOUND\n")
        return render_template("nodonation.html")

    # checks for if feedback already exists
    if databasequeries[0][1]:
        app.logger.info("\n--LOG: FEEDBACK ALREADY RECORDED\n")
        return render_template("invalid.html", identifier=fid)

    return render_template("valid.html", fid=fid, femail=femail)


@app.route("/feedback")
def feedbackbymail():
    token = request.args.get("token")
    try:
        uuid.UUID(token)
    except ValueError:
        return render_template("nodonation.html")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(SQL3.format(token=token))
    donation = cur.fetchall()
    app.logger.info("\n--log: {0}\n".format(donation))
    cur.close()
    conn.close()
    if not donation:
        return render_template("nodonation.html")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(SQL4.format(fid=donation[0][0]))
    priordonation = cur.fetchall()
    app.logger.info("\n--log: {0}\n".format(priordonation))
    cur.close()
    conn.close()
    if priordonation[0][0]:
        return render_template("invalid.html", identifier=donation[0][0])
    return render_template("valid.html", fid=donation[0][0], femail=donation[0][1])


@app.route("/store/<string:fid>", methods=["POST"])
def store(fid: str) -> str:
    answer1 = request.form["answer1"]
    name = request.form["name"]
    if not answer1 or not name:
        name = "Anonymous"
        return render_template("thank_you.html")

    answer2 = request.form["answer2"]
    email = request.form["email"]
    if not email or not answer2:
        email = "-"

    answer3 = request.form["answer3"]
    notification_email = request.form["notification_email"]
    if not notification_email or not answer2:
        notification_email = "-"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        SQL2.format(
            fid=fid,
            ans1=answer1,
            name=name,
            ans2=answer2,
            mail1=email,
            ans3=answer3,
            mail2=notification_email,
        )
    )
    cur.close()
    conn.commit()
    conn.close()
    app.logger.info("\n--LOG: stored in db\n")

    if notification_email:
        sendmail(notification_email)

    return render_template("thank_you.html")
