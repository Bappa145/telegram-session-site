from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

app = Flask(__name__)

API_ID = 27078605  # <-- নিজের API_ID বসাও
API_HASH = "52699dafb896a139789c88bc5c52f499"  # <-- নিজের API_HASH বসাও

sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get("phone")

    async def process():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        sessions[phone] = client

    try:
        asyncio.run(process())
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")

    client = sessions.get(phone)
    if not client:
        return jsonify({"status": "error", "message": "No session found for this phone."})

    async def login():
        await client.sign_in(phone, code)
        string_session = client.session.save()
        await client.disconnect()
        return string_session

    try:
        session_string = asyncio.run(login())
        return jsonify({"status": "ok", "session": session_string})
    except SessionPasswordNeededError:
        return jsonify({"status": "error", "message": "2FA password required!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
