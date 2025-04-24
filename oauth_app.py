from flask import Flask, redirect, request, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "mysecretkey123")

# ✅ อ่านจาก Environment Variable
CLIENT_ID = os.environ.get("FB_CLIENT_ID", "8312273118897670")
CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET", "cec15aac65268588acec3a23cb7d4e4b")
REDIRECT_URI = os.environ.get("FB_REDIRECT_URI", "https://facebook-api-8htt.onrender.com/callback")

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

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return '❌ ไม่พบ code ที่ได้จาก Facebook', 400

    token_url = 'https://graph.facebook.com/v22.0/oauth/access_token'
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'client_secret': CLIENT_SECRET,
        'code': code
    }

    token_resp = requests.get(token_url, params=params).json()
    access_token = token_resp.get('access_token')

    if not access_token:
        return jsonify
