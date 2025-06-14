
from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio

# Replace these with your own values from my.telegram.org
api_id = 123456  # <-- Replace with your API ID
api_hash = 'your_api_hash_here'  # <-- Replace with your API HASH

app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/')
def index():
    return """
           <form action='/get-session' method='post'>
               <input name='phone' placeholder='Enter Telegram Phone Number (+880...)'><br>
               <input name='code' placeholder='Enter OTP Code (if already received)'><br>
               <button type='submit'>Generate Session</button>
           </form>
           """

@app.route('/get-session', methods=['POST'])
def get_session():
    phone = request.form.get('phone')
    code = request.form.get('code')

    async def create_session():
        session = StringSession()
        async with TelegramClient(session, api_id, api_hash) as client:
            if not code:
                await client.send_code_request(phone)
                return "OTP sent to Telegram. Please input the code in the form."
            else:
                await client.sign_in(phone, code)
                return session.save()

    result = loop.run_until_complete(create_session())
    return jsonify({'session': result})

if __name__ == '__main__':
    app.run(debug=True)
