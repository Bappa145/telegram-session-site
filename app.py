from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

app = Flask(__name__)

API_ID = 27078605  # এখানে তোমার API ID বসাও
API_HASH = '52699dafb896a139789c88bc5c52f499'  # এখানে তোমার API HASH বসাও

clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')

    async def async_send_code():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        clients[phone] = client

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_send_code())
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        loop.close()

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')

    async def async_verify():
        client = clients.get(phone)
        if not client:
            raise Exception("Client not found")
        await client.connect()
        await client.sign_in(phone=phone, code=code)
        session_string = client.session.save()
        await client.disconnect()
        return session_string

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        session_string = loop.run_until_complete(async_verify())
        return jsonify({'status': 'ok', 'session': session_string})
    except SessionPasswordNeededError:
        return jsonify({'status': 'error', 'message': '2FA password required'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        loop.close()

if __name__ == '__main__':
    app.run(debug=True)
