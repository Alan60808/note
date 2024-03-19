import datetime
import time
import requests
import json

# 設定 Line Bot 的 Channel Access Token 和 Channel Secret
channel_access_token = '60c382a7a969d7c0a80e26d8c792d34f'
channel_secret = '3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU='

# 設定 Line Bot 的使用者 ID
user_id = "記事本小幫手"

# 設定提醒時間
remind_time = datetime.datetime.now() + datetime.timedelta(minutes=5)

# 建立 Line Bot 的訊息
message = {
    "type": "text",
    "text": "提醒您：5 分鐘後要吃藥了！"
}

# 發送 Line Bot 訊息
headers = {
    "Authorization": "Bearer " + channel_access_token,
}
requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps({"to": user_id, "messages": [message]}))

# 等待提醒時間到來
while datetime.datetime.now() < remind_time:
    time.sleep(1)

# 發送提醒訊息
requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps({"to": user_id, "messages": [message]}))
