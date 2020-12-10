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

#herokuの環境変数に設定された、LINE DevelopersのアクセストークンとChannelSecretを
#取得するコード
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

YOUR_APEX_API_KEY = os.environ["YOUR_APEX_API_KEY"]
YOUR_APEX_API_SECRET = os.environ["YOUR_APEX_API_SECRET"]
apex_api_key = YOUR_APEX_API_KEY
params = {"TRN-Api-Key":YOUR_APEX_API_SECRET}

#herokuへのデプロイが成功したかどうかを確認するためのコード
@app.route("/")
def hello_world():
    return "hello world!"

#LINE DevelopersのWebhookにURLを指定してWebhookからURLにイベントが送られるようにする
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

#以下でWebhookから送られてきたイベントをどのように処理するかを記述する
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    base_url = "https://public-api.tracker.gg/v2/apex/standard/"
    userinfo = event.message.text
    endpoint = "profile/" + userinfo
    # endpoint = "profile/origin/ユーザーネーム/"
    rank_result = []

    session = requests.Session()
    req = session.get(base_url+endpoint,params=params)
    print(req.status_code)

    req.close()
    res = json.loads(req.text)
    #pprint(res)

    rank_result.append("ID: "+str(res["data"]["platformInfo"]['platformUserId']))
    rank_result.append("Level: "+str(res["data"]["segments"][0]["stats"]["level"]["displayValue"]))
    rank_result.append(
        "RP: "+str(int(res["data"]["segments"][0]["stats"]["rankScore"]["value"]))
        +" - "
        +str(res["data"]["segments"][0]["stats"]["rankScore"]["metadata"]["rankName"]))
    rank_result.append("Rank: "+str(res["data"]["segments"][0]["stats"]["rankScore"]["rank"])+"位")
    #rank_result.append("Percentile: "+str(1000 - res["data"]["segments"][0]["stats"]["rankScore"]["percentile"]*10)+"%")
    rank_result = "\n".join(rank_result)

    #print("Kills:",res["data"]["segments"][0]["stats"]["kills"]["displayValue"])
    #pprint(res["data"]["segments"][0])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(rank_result)))


# ポート番号の設定
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)