from flask import Flask, render_template, request, redirect, url_for, session
from telethon.sync import TelegramClient
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_code', methods=['POST'])
def send_code():
    session['phone'] = request.form['phone']
    session['api_id'] = int(request.form['api_id'])
    session['api_hash'] = request.form['api_hash']

    client = TelegramClient('anon', session['api_id'], session['api_hash'])
    client.connect()
    client.send_code_request(session['phone'])
    client.disconnect()

    return redirect(url_for('verify'))

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/submit_code', methods=['POST'])
def submit_code():
    code = request.form['code']

    client = TelegramClient('anon', session['api_id'], session['api_hash'])
    client.connect()
    client.sign_in(session['phone'], code)
    client.disconnect()

    return "✅ Session created successfully and saved as 'anon.session'"

if __name__ == '__main__':
    app.run(debug=True)
