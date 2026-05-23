from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import time

app = Flask(__name__)

# ENV kontrol (500 hatasını engeller)
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")

if not TWILIO_SID or not TWILIO_TOKEN:
    print("TWILIO ENV MISSING!")
    client = None
else:
    client = Client(TWILIO_SID, TWILIO_TOKEN)

# Basit API KEY sistemi
API_KEYS = {
    "demo123": {
        "limit": 50,
        "used": 0,
        "last_request": 0
    }
}

# LOG sistemi
logs = []

@app.route("/")
def home():
    return "SMS SaaS v1 running"

@app.route("/send", methods=["POST"])
def send_sms():

    if client is None:
        return jsonify({"error": "Twilio not configured"}), 500

    api_key = request.form.get("api_key")
    number = request.form.get("number")
    text = request.form.get("text")

    # validation
    if not api_key or api_key not in API_KEYS:
        return jsonify({"error": "Invalid API key"}), 403

    if not number or not text:
        return jsonify({"error": "Missing parameters"}), 400

    user = API_KEYS[api_key]

    # rate limit (spam engel)
    now = time.time()
    if now - user["last_request"] < 1.5:
        return jsonify({"error": "Too many requests"}), 429

    user["last_request"] = now

    # limit kontrol
    if user["used"] >= user["limit"]:
        return jsonify({"error": "Limit exceeded"}), 403

    try:
        message = client.messages.create(
            body=text,
            from_="+15086875183",
            to=number
        )

        user["used"] += 1

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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs")
def get_logs():
    return jsonify(logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
