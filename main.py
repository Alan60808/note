from flask import Flask, request, abort
import json, requests, logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    StickerSendMessage, ImageSendMessage, LocationSendMessage
)

app = Flask(__name__)

# 環境變數，應從環境配置中獲取
access_token = 'xjU2mBe3bYiy8tpJn6IWvz6XiR6FFScP3aIZyVpUf6EVOs5rjzhqQ12Ilo7nyTlObMxSLci/ijo2dVD+fn7RPx/A09kFyee1dt5M/Yby/6IbrMr4n+aPnza9DSTxqYfNURpwZWHFR6TE6VA3OaqDWAdB04t89/1O/w1cDnyilFU='
channel_secret = '8ca4d5cc38858c4ee059f804550c3b4a'

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Received request: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    except LineBotApiError as e:
        app.logger.error(f'API error: {e}')
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply_token = event.reply_token

    if text.startswith('bike'):
        station_name = text.split(' ', 1)[1] if len(text.split(' ', 1)) > 1 else None
        if station_name:
            get_bike_info_msg = bike_info(station_name)
            line_bot_api.reply_message(reply_token, TextSendMessage(text=get_bike_info_msg))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入完整的站名，例如：'bike 文心森林公園'"))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="若需要查詢自行車站點信息，請使用 'bike 站名' 的格式，例如：'bike 文心森林公園'"))

def bike_info(input_sname):
    url = 'https://datacenter.taichung.gov.tw/swagger/OpenData/86dfad5c-540c-4479-bb7d-d7439d34eeb1'
    response = requests.get(url)
    data = response.json()
    matched_data = None
    for row in data["retVal"]:
        if row["sna"].startswith(input_sname) or input_sname in row["sna"]:
            matched_data = row
            break
    if matched_data:
        sna = matched_data["sna"]
        tot = matched_data["tot"]
        sbi = matched_data["sbi"]
        bemp = matched_data["bemp"]
        result = f"{sna} 車位數：{tot} 車輛數：{sbi} 空位數：{bemp}"
    else:
        similar_names = [row["sna"] for row in data["retVal"] if input_sname in row["sna"]]
        if similar_names:
            result = f"未找到 {input_sname} 相關的資料，建議您查詢：{', '.join(similar_names)}"
        else:
            result = f"未找到 {input_sname} 相關的資料"
    return result

print(bike_info("文心森林公園"))

if __name__ == "__main__":
    app.run()
