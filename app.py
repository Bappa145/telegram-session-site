from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

app = Flask(__name__)

API_ID = 27078605  # তোমার API ID বসাও
API_HASH = '52699dafb896a139789c88bc5c52f499'  # তোমার API HASH বসাও

phone_code_dict = {}  # ফোন নাম্বারের সাথে কোড match করার জন্য

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
        phone_code_dict[phone] = {
            'code_hash': sent.phone_code_hash
        }
        await client.disconnect()
        return True

    try:
        asyncio.run(send())
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')

    async def verify():
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            await client.sign_in(phone=phone, code=code)
            session_string = client.session.save()
            return session_string
        except SessionPasswordNeededError:
            return '2FA'
        finally:
            await client.disconnect()

    try:
        result = asyncio.run(verify())
        if result == '2FA':
            return jsonify({'status': 'error', 'message': '2FA password required'})
        return jsonify({'status': 'ok', 'session': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
