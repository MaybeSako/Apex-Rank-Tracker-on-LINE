from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
from pprint import pprint
import sys
import json
import requests

app = Flask(__name__)

# LINE Bot API values
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Tracker Network API values
YOUR_APEX_API_KEY = os.environ["YOUR_APEX_API_KEY"]
params = {"TRN-Api-Key":YOUR_APEX_API_KEY}

# herokuへのデプロイが成功したかどうかを確認するためのコード
@app.route("/")
def hello_world():
    return "hello world!"

# LINE DevelopersのWebhookにURLを指定してWebhookからURLにイベントが送られるようにする
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し、問題なければhandleに定義されている関数を呼ぶ
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 以下でWebhookから送られてきたイベントをどのように処理するかを記述する
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    base_url = "https://public-api.tracker.gg/v2/apex/standard/"
    endpoint = "profile/" + userinfo
    session = requests.Session()
    req = session.get(base_url+endpoint,params=params)
    req.close()
    res = json.loads(req.text)

    # Refining the result from Tracker Network API
    rank_result = []
    player_id = res["data"]["platformInfo"]['platformUserId']
    player_level = res["data"]["segments"][0]["stats"]["level"]["displayValue"]
    player_rank_name = res["data"]["segments"][0]["stats"]["rankScore"]["metadata"]["rankName"]
    player_rp = res["data"]["segments"][0]["stats"]["rankScore"]["value"]
    player_rank_position = res["data"]["segments"][0]["stats"]["rankScore"]["rank"]
    player_percentile = res["data"]["segments"][0]["stats"]["rankScore"]["percentile"]

    rank_result.append("ID: " + str(player_id))
    rank_result.append("Level: " + str(player_level))
    rank_result.append("Rank: " + str(player_rank_name))
    rank_result.append("RP: " + str(player_rp))
    rank_result.append("Rank Position: " + str(player_rank_position) + "位")
    # The value of percentile is occasioanlly returned as None
    if player_percentile is None:
        pass
    else:
        rank_result.append("RP: " + str(player_percentile))

    rank_result = "\n".join(rank_result)
    print(rank_result)

# ポート番号の設定
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)