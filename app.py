from flask import Flask, request, render_template, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio

# এখানে তোমার Telegram API ID ও Hash বসাও
api_id = 27078605       # <-- Replace this
api_hash = '52699dafb896a139789c88bc5c52f499'  # <-- Replace this

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-session', methods=['POST'])
def get_session():
    phone = request.form.get('phone')
    code = request.form.get('code')

    async def generate():
        session = StringSession()
        async with TelegramClient(session, api_id, api_hash) as client:
            if not code:
                await client.send_code_request(phone)
                return "OTP sent! Re-enter the code and submit again."
            else:
                await client.sign_in(phone, code)
                return session.save()

    result = loop.run_until_complete(generate())
    return jsonify({'session': result})

if __name__ == '__main__':
    app.run(debug=True)
