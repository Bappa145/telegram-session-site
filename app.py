from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

app = Flask(__name__)

# 🔐 Replace these with your own API ID and HASH from https://my.telegram.org
API_ID = 27078605
API_HASH = '52699dafb896a139789c88bc5c52f499'

# Store phone -> client mapping temporarily
clients = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'status': 'error', 'message': 'Phone number missing'})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = TelegramClient(StringSession(), API_ID, API_HASH, loop=loop)
    clients[phone] = client

    try:
        loop.run_until_complete(client.connect())
        loop.run_until_complete(client.send_code_request(phone))
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')

    if not (phone and code):
        return jsonify({'status': 'error', 'message': 'Phone or code missing'})

    client = clients.get(phone)

    if not client:
        return jsonify({'status': 'error', 'message': 'Client not found'})

    loop = client.loop

    try:
        loop.run_until_complete(client.sign_in(phone=phone, code=code))

        session_string = client.session.save()
        return jsonify({'status': 'ok', 'session': session_string})
    except SessionPasswordNeededError:
        return jsonify({'status': 'error', 'message': '2FA password required'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        loop.run_until_complete(client.disconnect())

if __name__ == '__main__':
    app.run(debug=True)
