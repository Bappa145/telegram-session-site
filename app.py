from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

# Config
API_ID = 27078605  # Replace with your API ID
API_HASH = '52699dafb896a139789c88bc5c52f499'  # Replace with your API HASH

app = Flask(__name__)
clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client = TelegramClient(StringSession(), API_ID, API_HASH, loop=loop)
    clients[phone] = client

    async def send():
        await client.connect()
        await client.send_code_request(phone)

    loop.run_until_complete(send())
    return jsonify({'status': 'ok'})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')

    client = clients.get(phone)

    if not client:
        return jsonify({'status': 'error', 'message': 'Client not found'}), 400

    loop = client.loop

    async def verify():
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            return {'status': 'error', 'message': '2FA password needed'}
        session_str = client.session.save()
        await client.disconnect()
        return {'session': session_str}

    result = loop.run_until_complete(verify())
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
