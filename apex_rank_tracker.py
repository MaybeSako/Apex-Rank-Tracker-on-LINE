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
    # Check if user input is correct
    if not get_stats(event.message.text):
        result_message = "Wrong ID, Check your input"
    else:
        pass
        result_message = get_stats(event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_message)
    )

def get_stats(user_information):
    base_url = "https://public-api.tracker.gg/v2/apex/standard/"
    endpoint = "profile/" + user_information
    session = requests.Session()
    req = session.get(base_url + endpoint, params=params)
    req.close()
    res = json.loads(req.text)

    # Refine the result from Tracker Network API
    player_id = res["data"]["platformInfo"]['platformUserId']
    player_level = res["data"]["segments"][0]["stats"]["level"]["displayValue"]
    rank_name = res["data"]["segments"][0]["stats"]["rankScore"]["metadata"]["rankName"]
    ranked_point = res["data"]["segments"][0]["stats"]["rankScore"]["value"]
    rank_position = res["data"]["segments"][0]["stats"]["rankScore"]["rank"]
    player_percentile = res["data"]["segments"][0]["stats"]["rankScore"]["percentile"]

    rank_result = []
    rank_result.append("ID: " + str(player_id))
    rank_result.append("Level: " + str(player_level))
    rank_result.append("Rank: " + str(rank_name))
    rank_result.append("RP: " + str(ranked_point))
    rank_result.append("Rank Position: " + str(rank_position) + "位")
    # The value of percentile is occasioanlly returned as None
    rank_result.append("Percentile: Percentile is currently not available") if player_percentile is None else rank_result.append("RP Percentile: " + str(player_percentile))

    rank_result = "\n".join(rank_result)
    return rank_result

# ポート番号の設定
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)