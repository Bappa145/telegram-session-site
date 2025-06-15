from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio
import nest_asyncio

nest_asyncio.apply()
loop = asyncio.get_event_loop()

app = Flask(__name__)

API_ID = 27078605  # Replace with your API ID
API_HASH = '52699dafb896a139789c88bc5c52f499'  # Replace with your API HASH

# Store phone_code_hash for each phone temporarily
phone_code_hash_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')

    async def send():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        sent = await client.send_code_request(phone)
        phone_code_hash_store[phone] = sent.phone_code_hash
        await client.disconnect()
        return sent.phone_code_hash

    try:
        code_hash = loop.run_until_complete(send())
        return jsonify({'status': 'ok', 'phone_code_hash': code_hash})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')
    phone_code_hash = phone_code_hash_store.get(phone)

    if not phone_code_hash:
        return jsonify({'status': 'error', 'message': 'Missing phone_code_hash'})

    async def verify():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        session_string = client.session.save()
        await client.disconnect()
        return session_string

    try:
        session = loop.run_until_complete(verify())
        return jsonify({'status': 'ok', 'session': session})
    except SessionPasswordNeededError:
        return jsonify({'status': 'error', 'message': '2FA password required'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
