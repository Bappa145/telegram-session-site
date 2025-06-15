from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio

api_id = '27078605'
api_hash = '52699dafb896a139789c88bc5c52f499'

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

session_dict = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data['phone']
    client = TelegramClient(StringSession(), api_id, api_hash, loop=loop)
    session_dict[phone] = client

    async def main():
        await client.connect()
        await client.send_code_request(phone)
        return jsonify({'status': 'ok'})

    return loop.run_until_complete(main())

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data['phone']
    code = data['code']
    client = session_dict.get(phone)
    if not client:
        return jsonify({'message': 'Session not found'}), 400

    async def main():
        try:
            await client.connect()
            await client.sign_in(phone, code)
            session_str = client.session.save()
            return jsonify({'session': session_str})
        except SessionPasswordNeededError:
            return jsonify({'message': '2FA password required'})
        except Exception as e:
            return jsonify({'message': str(e)})

    return loop.run_until_complete(main())

if __name__ == '__main__':
    app.run(debug=True)
