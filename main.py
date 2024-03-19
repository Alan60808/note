import requests
import pyrtklib
from linebot import LineBotApi, WebhookHandler

# 設定 Line Bot 資訊
line_bot_api = LineBotApi('3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU=')
line_bot_handler = WebhookHandler('60c382a7a969d7c0a80e26d8c792d34f')

# 設定 API 位址
url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001'

# 設定參數
params = {
    'Authorization': 'CWB-7E7194B4-1234-4567-8901-234567890123'
}

# 設定 DGPS 設定
dgps_settings = {
    'base_station_id': '0000',
    'mount_point': 'RTCM3',
    'stream_url': 'http://127.0.0.1:10000'
}

# 建立 DGPS 接收器
receiver = pyrtklib.Receiver(dgps_settings)

# 開始接收 DGPS 資料
receiver.start()

# 設定 Webhook 路由
@line_bot_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 取得使用者輸入的文字
    text = event.message.text

    # 檢查使用者輸入的文字
    if text == '天氣':

        # 取得 GPS 定位
        while True:
            # 讀取 DGPS 資料
            data = receiver.read()

            # 檢查資料是否有效
            if data is None:
                continue

            # 取得位置座標
            latitude = data['lat']
            longitude = data['lon']

            # 設定位置名稱
            location_name = geocoder.reverse([latitude, longitude]).city

            # 更新參數
            params['locationName'] = location_name

            # 發送 API 請求
            response = requests.get(url, params=params)

            # 檢查 API 回應狀態
            if response.status_code == 200:

                # 解析 JSON 資料
                data = response.json()

                # 取得天氣狀況
                weather = data['records']['location'][0]['weatherElement'][0]['time'][0]['parameter'][0]['value']

                # 回覆訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    text=f'{location_name}目前天氣：{weather}'
                )

            else:

                # 印出錯誤訊息
                print(f'API 回應錯誤：{response.status_code}')

    else:

        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            text='請輸入「天氣」查詢天氣狀況'
        )

# 啟動 Line Bot
line_bot_handler.run()
