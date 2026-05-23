@app.route('/send', methods=['POST'])
def send_sms():
    try:
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

    except Exception as e:
        return {
            "error": str(e)
        }, 500
