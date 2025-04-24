from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ✅ ใส่ Access Token ที่ได้จาก Facebook Graph API Explorer
ACCESS_TOKEN = 'EAAThQXZCTvaQBO6rrNzQAx4pQrKEJY...'  # <-- เปลี่ยนตรงนี้

@app.route('/ads', methods=['GET'])
def get_ads():
    account_id = request.args.get('account_id')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    insights_url = (
        f"https://graph.facebook.com/v22.0/{account_id}/insights"
        f"?fields=campaign_name,adset_name,ad_name,ad_id,impressions,clicks,spend"
        f"&level=ad&time_range[since]={date_start}&time_range[until]={date_end}"
        f"&limit=100&access_token={ACCESS_TOKEN}"
    )

    response = requests.get(insights_url)
    data = response.json()
    results = []

    for ad in data.get('data', []):
        ad_id = ad['ad_id']
        ad_name = ad['ad_name']
        spend = ad['spend']

        # ดึง creative id
        creative_url = f"https://graph.facebook.com/v22.0/{ad_id}?fields=creative&access_token={ACCESS_TOKEN}"
        creative_resp = requests.get(creative_url).json()
        creative_id = creative_resp.get('creative', {}).get('id', '')

        image_url = ''
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
            'image_url': image_url
        })

    return jsonify(results)

# ✅ สำหรับ Render.com ต้องใช้ host='0.0.0.0' และ port จาก ENV
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
