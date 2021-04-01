
import numpy as np
player_rank = "Silver 2"
ranked_point = 2008

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

next_rank_number = int(player_rank[-1]) - 1
next_rank_name = next_rank_title + " " + str(next_rank_number)

next_rank_value = min([value for value in RP_list if value > ranked_point])
remaining_RP = next_rank_value - ranked_point

print("次のランク：", next_rank_name, "まで残り RP:", remaining_RP)