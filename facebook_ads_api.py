from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔐 ใส่ Access Token ที่ได้จาก Graph API Explorer หรือ OAuth
ACCESS_TOKEN = 'EAAThQXZCTvaQBO7AnmzYR7ZAhlPFJVrM6tJSCWzZBgr4dZAyjza8extSKWiY8hVgQ5qyJoYr39hyVTDpUgv4RaQnRJ9VrggNA5adNs0P1DA733fiMfy0yCw9UpRJZBs8FdEFgqynj2TMqRcBeu83ZCygZCbbovDRV9WZCqiddRKr6dyqv4zUC3ZCebQZBG0Fr5iquQ2NSO75gPQjQx1Akgi6iD3zeZCMH9gZB16wYZAYUpOMWpDcZD'  # <-- ใส่ token จริงของคุณ

@app.route('/ads', methods=['GET'])
def get_ads():
    account_id = request.args.get('account_id')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    if not all([account_id, date_start, date_end]):
        return jsonify({"error": "Missing required query parameters"}), 400

    insights_url = (
        f"https://graph.facebook.com/v22.0/{account_id}/insights"
        f"?fields=campaign_name,adset_name,ad_name,ad_id,impressions,clicks,spend"
        f"&level=ad&time_range[since]={date_start}&time_range[until]={date_end}"
        f"&limit=100&access_token={ACCESS_TOKEN}"
    )

    response = requests.get(insights_url)
    data = response.json()

    if 'error' in data:
        return jsonify({"error": data['error']}), 400

    if not data.get('data'):
        return jsonify({"message": "No ad data found for the given date range."}), 200

    results = []

    for ad in data['data']:
        ad_id = ad.get('ad_id')
        ad_name = ad.get('ad_name')
        spend = ad.get('spend')
        image_url = ''

        # 🔍 ดึง Creative ID
        creative_url = f"https://graph.facebook.com/v22.0/{ad_id}?fields=creative&access_token={ACCESS_TOKEN}"
        creative_resp = requests.get(creative_url).json()
        creative_id = creative_resp.get('creative', {}).get('id', '')

        if creative_id:
            detail_url = f"https://graph.facebook.com/v22.0/{creative_id}?fields=object_story_spec&access_token={ACCESS_TOKEN}"
            detail_resp = requests.get(detail_url).json()
            spec = detail_resp.get('object_story_spec', {})
            if 'link_data' in spec:
                image_url = spec['link_data'].get('image_url', '')

        results.append({
            'ad_id': ad_id,
            'ad_name': ad_name,
            'spend': spend,
            'image_url': image_url or "NO IMAGE"
        })

    return jsonify(results)

# ✅ ตั้งค่าให้ Render ใช้ PORT ที่กำหนด
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
