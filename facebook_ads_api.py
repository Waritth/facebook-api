from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/ads/insights')
def get_ads_insights():
    access_token = request.args.get('access_token')
    ad_account_id = request.args.get('ad_account_id')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    if not all([access_token, ad_account_id, date_start, date_end]):
        return jsonify({'error': 'Missing parameters'}), 400

    insights_url = (
        f"https://graph.facebook.com/v22.0/{ad_account_id}/insights"
        f"?fields=ad_id,ad_name,impressions,clicks,spend,ad_creative_id"
        f"&level=ad&time_range[since]={date_start}&time_range[until]={date_end}"
        f"&limit=100&access_token={access_token}"
    )

    insights_resp = requests.get(insights_url).json()
    if 'error' in insights_resp:
        return jsonify(insights_resp), 400

    results = []

    for ad in insights_resp.get("data", []):
        ad_id = ad.get("ad_id")
        ad_name = ad.get("ad_name")
        spend = ad.get("spend")
        creative_id = ad.get("ad_creative_id", '')
        image_url = "NO IMAGE"

        if creative_id:
            creative_url = f"https://graph.facebook.com/v22.0/{creative_id}?fields=object_story_spec,object_story_id&access_token={access_token}"
            creative_resp = requests.get(creative_url).json()

            link_data = creative_resp.get("object_story_spec", {}).get("link_data", {})
            if link_data:
                image_url = link_data.get("image_url", image_url)

            story_id = creative_resp.get("object_story_id")
            if story_id:
                story_url = f"https://graph.facebook.com/v22.0/{story_id}?fields=attachments&access_token={access_token}"
                story_resp = requests.get(story_url).json()
                attachments = story_resp.get("attachments", {}).get("data", [])
                if attachments:
                    image_url = (
                        attachments[0].get("media", {}).get("image", {}).get("src")
                        or attachments[0].get("thumbnail_url", image_url)
                    )

        results.append({
            "ad_id": ad_id,
            "ad_name": ad_name,
            "spend": spend,
            "image_url": image_url
        })

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
