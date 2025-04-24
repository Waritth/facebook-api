from flask import Flask, redirect, request, session, jsonify
import requests
import os
from dotenv import load_dotenv

# 🔄 โหลดค่า .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("FB_REDIRECT_URI")

# 🌐 Step 1: เริ่ม Login
@app.route('/')
def index():
    fb_auth_url = (
        f'https://www.facebook.com/v22.0/dialog/oauth'
        f'?client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope=pages_show_list,pages_read_engagement,ads_read'
        f'&response_type=code'
    )
    return redirect(fb_auth_url)

# 🔁 Step 2: Callback
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code from Facebook'}), 400

    token_url = 'https://graph.facebook.com/v22.0/oauth/access_token'
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'client_secret': CLIENT_SECRET,
        'code': code
    }

    resp = requests.get(token_url, params=params).json()
    access_token = resp.get('access_token')

    if not access_token:
        return jsonify({'error': 'Failed to obtain access token', 'response': resp}), 400

    session['access_token'] = access_token

    return jsonify({
        'message': '✅ Login successful',
        'access_token': access_token
    })

# ✅ ดึงข้อมูลเพจ
@app.route('/me/accounts')
def get_pages():
    token = session.get('access_token')
    if not token:
        return jsonify({'error': 'Login first'}), 401

    response = requests.get(
        'https://graph.facebook.com/v22.0/me/accounts',
        params={'access_token': token}
    )
    return jsonify(response.json())

# 🔽 เริ่มต้น Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
