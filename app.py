from flask import Flask, request
from twilio.rest import Client
import os

app = Flask(__name__)

account_sid = os.environ.get("TWILIO_SID")
auth_token = os.environ.get("TWILIO_TOKEN")

client = Client(account_sid, auth_token)

@app.route('/')
def home():
    return 'SMS API AKTIF'

@app.route('/send', methods=['POST'])
def send_sms():
    number = request.form['number']
    text = request.form['text']

    message = client.messages.create(
        body=text,
        from_='+15086875183',
        to=number
    )

    return {
        "status": "success",
        "sid": message.sid
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
