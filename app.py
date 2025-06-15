app.py

from flask import Flask, request, jsonify, render_template from telethon.sync import TelegramClient from telethon.sessions import StringSession from telethon.errors import SessionPasswordNeededError import asyncio

app = Flask(name)

API_ID = 123456  # <-- তোমার API ID বসাও API_HASH = 'your_api_hash'  # <-- তোমার API HASH বসাও

sessions = {}

@app.route('/') def index(): return render_template('index.html')

@app.route('/send-code', methods=['POST']) def send_code(): data = request.get_json() phone = data.get("phone")

async def process():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        await client.send_code_request(phone)
        sessions[phone] = client.session.save()

try:
    asyncio.new_event_loop().run_until_complete(process())
    return jsonify({"status": "ok"})
except Exception as e:
    return jsonify({"status": "error", "message": str(e)})

@app.route('/verify-code', methods=['POST']) def verify_code(): data = request.get_json() phone = data.get("phone") code = data.get("code") session_string = sessions.get(phone)

if not session_string:
    return jsonify({"status": "error", "message": "No session found for this phone"})

async def verify():
    async with TelegramClient(StringSession(session_string), API_ID, API_HASH) as client:
        await client.sign_in(phone, code)
        return client.session.save()

try:
    new_session = asyncio.new_event_loop().run_until_complete(verify())
    return jsonify({"status": "ok", "session": new_session})
except SessionPasswordNeededError:
    return jsonify({"status": "error", "message": "2FA password required!"})
except Exception as e:
    return jsonify({"status": "error", "message": str(e)})

if name == 'main': app.run(debug=True)

