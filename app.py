from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import os
import secrets

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

account_sid = os.environ.get("TWILIO_SID")
auth_token = os.environ.get("TWILIO_TOKEN")

client = Client(account_sid, auth_token)

# =========================
# DATABASE MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    api_key = db.Column(db.String(200), unique=True)

class SmsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    number = db.Column(db.String(50))
    message = db.Column(db.String(500))
    status = db.Column(db.String(50))

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "SMS API AKTIF"

# =========================
# CREATE USER
# =========================

@app.route("/create_user", methods=["POST"])
def create_user():

    username = request.form.get("username")

    if not username:
        return jsonify({
            "error": "username gerekli"
        })

    existing = User.query.filter_by(username=username).first()

    if existing:
        return jsonify({
            "error": "user zaten var"
        })

    api_key = secrets.token_hex(16)

    new_user = User(
        username=username,
        api_key=api_key
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "username": username,
        "api_key": api_key
    })

# =========================
# SEND SMS
# =========================

@app.route("/send", methods=["POST"])
def send_sms():

    api_key = request.form.get("api_key")
    number = request.form.get("number")
    text = request.form.get("text")

    if not api_key:
        return jsonify({
            "error": "api_key gerekli"
        })

    user = User.query.filter_by(api_key=api_key).first()

    if not user:
        return jsonify({
            "error": "gecersiz api key"
        })

    try:

        message = client.messages.create(
            body=text,
            from_="+15086875183",
            to=number
        )

        log = SmsLog(
            user_id=user.id,
            number=number,
            message=text,
            status="sent"
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({
            "status": "success",
            "sid": message.sid
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })

# =========================
# GET LOGS
# =========================

@app.route("/logs", methods=["POST"])
def logs():

    api_key = request.form.get("api_key")

    user = User.query.filter_by(api_key=api_key).first()

    if not user:
        return jsonify({
            "error": "gecersiz api key"
        })

    logs = SmsLog.query.filter_by(user_id=user.id).all()

    result = []

    for log in logs:

        result.append({
            "number": log.number,
            "message": log.message,
            "status": log.status
        })

    return jsonify(result)

# =========================
# CREATE TABLES
# =========================

with app.app_context():
    db.create_all()

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
