from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import time

app = Flask(__name__)

client = Client(
    os.environ.get("TWILIO_SID"),
    os.environ.get("TWILIO_TOKEN")
)

# DEMO API KEY DATABASE
API_KEYS = {
    "demo123": {
        "limit": 10,
        "used": 0,
        "last_request": 0
    }
}

# SMS LOG
logs = []

@app.route("/")
def home():
    return "SMS SaaS V1 aktif"

@app.route("/send", methods=["POST"])
def send_sms():

    api_key = request.form.get("api_key")
    number = request.form.get("number")
    text = request.form.get("text")

    # 1. API KEY kontrol
    if api_key not in API_KEYS:
        return jsonify({"error": "Invalid API key"}), 403

    user = API_KEYS[api_key]

    # 2. rate limit (spam engel)
    now = time.time()
    if now - user["last_request"] < 2:
        return jsonify({"error": "Too fast requests"}), 429

    user["last_request"] = now

    # 3. limit kontrol
    if user["used"] >= user["limit"]:
        return jsonify({"error": "Limit exceeded"}), 403

    # 4. SMS gönder
    message = client.messages.create(
        body=text,
        from_="+15086875183",
        to=number
    )

    # 5. kullanım artır
    user["used"] += 1

    # 6. log kaydet
    logs.append({
        "api_key": api_key,
        "number": number,
        "text": text,
        "sid": message.sid,
        "time": now
    })

    return jsonify({
        "status": "success",
        "sid": message.sid,
        "used": user["used"]
    })

@app.route("/logs")
def get_logs():
    return jsonify(logs)
