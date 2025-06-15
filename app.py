from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import nest_asyncio
import asyncio

nest_asyncio.apply()
loop = asyncio.get_event_loop()
app = Flask(__name__)

API_ID = 123456  # ✅ তোমার API ID দাও
API_HASH = 'your_api_hash'  # ✅ তোমার API HASH দাও

# Global dict to store client and hash
client_store = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get("phone")

    async def run():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        sent = await client.send_code_request(phone)
        # Store the client & phone_code_hash together
        client_store[phone] = {
            "client": client,
            "phone_code_hash": sent.phone_code_hash
        }
        return sent.phone_code_hash

    try:
        phone_code_hash = loop.run_until_complete(run())
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")

    if phone not in client_store:
        return jsonify({'status': 'error', 'message': 'Session not found'})

    stored = client_store[phone]
    client = stored["client"]
    phone_code_hash = stored["phone_code_hash"]

    async def run():
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        session_string = client.session.save()
        await client.disconnect()
        return session_string

    try:
        session = loop.run_until_complete(run())
        return jsonify({'status': 'ok', 'session': session})
    except SessionPasswordNeededError:
        return jsonify({'status': 'error', 'message': '2FA password required'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
