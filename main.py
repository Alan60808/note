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
        app.logger.info("Handler processed successfully")
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
    app.logger.info(f"Received text: {text}")  # 確認收到的文字
    reply_token = event.reply_token

    if text.lower().startswith('bike'):
        station_name = text.split(' ', 1)[1] if len(text.split(' ', 1)) > 1 else None
        if station_name:
            get_bike_info_msg = bike_info(station_name)
            app.logger.info(f"Bike info message: {get_bike_info_msg}")  # 日誌輸出回應的數據
            try:
                line_bot_api.reply_message(reply_token, TextSendMessage(text=get_bike_info_msg))
                app.logger.info("Message sent successfully")
            except LineBotApiError as e:
                app.logger.error(f"Failed to send message: {e}")
                line_bot_api.reply_message(reply_token, TextSendMessage(text="發送訊息失敗，請稍後再試。"))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入完整的站名，例如：'bike 文心森林公園'"))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="若需要查詢自行車站點信息，請使用 'bike 站名' 的格式，例如：'bike 文心森林公園'"))

def bike_info(input_sname):
    app.logger.info(f"Searching for bike station: {input_sname}")  # 日誌輸出正在搜索的站名
    url = 'https://datacenter.taichung.gov.tw/swagger/OpenData/86dfad5c-540c-4479-bb7d-d7439d34eeb1'
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查HTTP請求是否成功
        data = response.json()
        for row in data["retVal"]:
            if input_sname in row["sna"]:
                sna = row["sna"]
                tot = row["tot"]
                sbi = row["sbi"]
                bemp = row["bemp"]
                result = f"{sna} 車位數：{tot} 車輛數：{sbi} 空位數：{bemp}"
                app.logger.info(f"Found station: {result}")  # 日誌輸出找到的站點信息
                return result
        result = f"未找到 {input_sname} 相關的資料"
        app.logger.info(f"Station not found: {result}")  # 日誌輸出未找到站點信息
        return result
    except requests.RequestException as e:
        app.logger.error(f"Error fetching bike info: {e}")
        return "無法獲取自行車站點信息，請稍後再試。"

if __name__ == "__main__":
    app.run(debug=True)


