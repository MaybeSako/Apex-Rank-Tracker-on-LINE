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
import numpy as np

app = Flask(__name__)

# LINE Bot API values
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Tracker Network API values
YOUR_APEX_API_KEY = os.environ["YOUR_APEX_API_KEY"]
params = {"TRN-Api-Key":YOUR_APEX_API_KEY}

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
    try:
        result_message = get_stats(str(event.message.text))
    except KeyError:
        result_message = "Invalid input. Make sure your platform and ID are correct."
    except json.decoder.JSONDecodeError:
        result_message = "Invalid input. Make sure your platform and ID are correct." 
    else:
        pass

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
    player_rank = res["data"]["segments"][0]["stats"]["rankScore"]["metadata"]["rankName"]
    ranked_point = res["data"]["segments"][0]["stats"]["rankScore"]["value"]
    rank_position = res["data"]["segments"][0]["stats"]["rankScore"]["rank"]
    player_percentile = res["data"]["segments"][0]["stats"]["rankScore"]["percentile"]

    rank_result = []
    rank_result.append("ID: " + str(player_id))
    rank_result.append("レベル: " + str(player_level))
    rank_result.append("ランク帯: " + str(player_rank))

    # np floor
    rank_result.append("RP: " + str(ranked_point))
    rank_result.append("ランクポイント順位: " + str(rank_position) + "位")
    # Value of percentile is occasioanlly returned as None
    rank_result.append("パーセンタイル: Percentile is currently not available") if player_percentile is None else rank_result.append("RP Percentile: " + str(player_percentile))

    rank_result = "\n".join(rank_result)
    return rank_result

def calculate_rp(player_rank, ranked_point):
    import numpy as np
    # player_rank = "Silver 1"
    # ranked_point = 2678

    if player_rank[0] == "B":
        RP_list = [1200, 900, 600, 300, 0]
        if player_rank[-1] == "1":
            next_player_rank = "Silver"
        else:
            next_player_rank = "Bronze"
    elif player_rank[0] == "S":
        RP_list = [2800, 2400, 2000, 1600, 1200]
        if player_rank[-1] == "1":
            next_player_rank = "Gold"
        else:
            next_player_rank = "Silver"
    elif player_rank[0] == "G":
        RP_list = [4800, 4300, 3800, 3300, 2800]
        if player_rank[-1] == "1":
            next_player_rank = "Platinum"
        else:
            next_player_rank = "Gold"
    elif player_rank[0] == "P":
        RP_list = [7200, 6600, 6000, 5400, 4800]
        if player_rank[-1] == "1":
            next_player_rank = "Diamond"
        else:
            next_player_rank = "Platinum"
    elif player_rank[0] == "D":
        RP_list = [10000, 9300, 8600, 7900, 7200]
        if player_rank[-1] == "1":
            next_player_rank = "Master"
        else:
            next_player_rank = "Diamond"

# RPとリストは差分ではなく、大小で判定
    remaining_RP = min(np.abs(np.array(RP_list) - ranked_point))
    next_player_rank = next_player_rank + " " + str(np.argmin(np.abs(np.array(RP_list) - ranked_point)) + 1)

    return("次のランク：", next_player_rank, "まで残り", remaining_RP, "RP")

print(calculate_rp("Silver 1", 2478))

# ポート番号の設定
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)