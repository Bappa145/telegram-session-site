from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio

app = Flask(__name__)

# ⛔️ Replace with your own credentials from https://my.telegram.org
API_ID = 27078605      # 🔁 তোমার API ID বসাও
API_HASH = '52699dafb896a139789c88bc5c52f499'  # 🔁 তোমার API HASH বসাও

# ✅ ফোন নাম্বার ও client স্টোর করার dict
phone_dict = {}
client_dict = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')
    
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(client.connect())
        loop.run_until_complete(client.send_code_request(phone))

        phone_dict[phone] = True
        client_dict[phone] = client

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')

    if not phone_dict.get(phone) or not client_dict.get(phone):
        return jsonify({'status': 'error', 'message': 'Session expired or phone not found'})

    client = client_dict[phone]

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(client.sign_in(phone, code))
        session_str = client.session.save()
        return jsonify({'session': session_str})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
