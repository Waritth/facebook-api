from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = 'EAAThQXZCTvaQBO7AnmzYR7ZAhlPFJVrM6tJSCWzZBgr4dZAyjza8extSKWiY8hVgQ5qyJoYr39hyVTDpUgv4RaQnRJ9VrggNA5adNs0P1DA733fiMfy0yCw9UpRJZBs8FdEFgqynj2TMqRcBeu83ZCygZCbbovDRV9WZCqiddRKr6dyqv4zUC3ZCebQZBG0Fr5iquQ2NSO75gPQjQx1Akgi6iD3zeZCMH9gZB16wYZAYUpOMWpDcZD'  # ใส่ Access Token จริง

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
        image_url = 'NO IMAGE'

        try:
            # 1. ดึง creative ID
            creative_url = f"https://graph.facebook.com/v22.0/{ad_id}?fields=creative&access_token={ACCESS_TOKEN}"
            creative_resp = requests.get(creative_url).json()
            creative_id = creative_resp.get('creative', {}).get('id', '')

            if creative_id:
                # 2. ดึงข้อมูลเพิ่มเติมของ creative
                detail_url = f"https://graph.facebook.com/v22.0/{creative_id}?fields=object_story_spec,object_story_id&access_token={ACCESS_TOKEN}"
                detail_resp = requests.get(detail_url).json()
                spec = detail_resp.get('object_story_spec', {})

                # ✅ กรณี 1: ถ้ามี image_url ใน link_data
                if 'link_data' in spec:
                    image_url = spec['link_data'].get('image_url', image_url)

                # ✅ กรณี 2: ดึงภาพจาก object_story_id (dark post)
                story_id = detail_resp.get('object_story_id')
                if story_id:
                    post_url = f"https://graph.facebook.com/v22.0/{story_id}?fields=message,attachments&access_token={ACCESS_TOKEN}"
                    post_resp = requests.get(post_url).json()

                    # 🔍 Log ดู post response เพื่อ debug
                    app.logger.info(f"🔍 Post response for {story_id}:\n{post_resp}")

                    attachments = post_resp.get('attachments', {}).get('data', [])
                    if attachments:
                        media = attachments[0].get('media', {})
                        image_data = media.get('image', {})
                        image_url = image_data.get('src') or attachments[0].get('thumbnail_url', image_url)

        except Exception as e:
            app.logger.error(f"❌ Error processing ad {ad_id}: {e}")

        results.append({
            'ad_id': ad_id,
            'ad_name': ad_name,
            'spend': spend,
            'image_url': image_url or 'NO IMAGE'
        })

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
