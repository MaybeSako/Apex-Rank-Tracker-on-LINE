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
    # rank_result.append("ランクポイント順位: " + str(rank_position) + "位")
    # Value of percentile is occasioanlly returned as None
    0 if player_percentile is None else rank_result.append("RP Percentile: " + str(player_percentile))

    rank_result.append(calculate_rp(player_rank, ranked_point))
    rank_result = "\n".join(rank_result)
    return rank_result

def calculate_rp(player_rank, ranked_point):
    if player_rank[0] == "B":
        RP_list = [1200, 900, 600, 300, 0]
        if player_rank[-1] == "1":
            next_rank_title = "Silver"
        else:
            next_rank_title = "Bronze"
    elif player_rank[0] == "S":
        RP_list = [2800, 2400, 2000, 1600, 1200]
        if player_rank[-1] == "1":
            next_rank_title = "Gold"
        else:
            next_rank_title = "Silver"
    elif player_rank[0] == "G":
        RP_list = [4800, 4300, 3800, 3300, 2800]
        if player_rank[-1] == "1":
            next_rank_title = "Platinum"
        else:
            next_rank_title = "Gold"
    elif player_rank[0] == "P":
        RP_list = [7200, 6600, 6000, 5400, 4800]
        if player_rank[-1] == "1":
            next_rank_title = "Diamond"
        else:
            next_rank_title = "Platinum"
    elif player_rank[0] == "D":
        RP_list = [10000, 9300, 8600, 7900, 7200]
        if player_rank[-1] == "1":
            next_rank_title = "Master"
        else:
            next_rank_title = "Diamond"

    next_rank_value = min([value for value in RP_list if value > ranked_point]) # 次のボーダーRP
    next_rank_number = RP_list.index(next_rank_value) + 0
    remaining_RP = next_rank_value - ranked_point
    if next_rank_number == 0:
        next_rank_number = 4

    goal_message = "次のランク：" + next_rank_title + " " + str(next_rank_number) + "　まで残り RP:" + str(remaining_RP)
    return goal_message

print(get_stats("origin/Sssakoo"))