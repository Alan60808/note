import json,requests,logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage

access_token = 'xjU2mBe3bYiy8tpJn6IWvz6XiR6FFScP3aIZyVpUf6EVOs5rjzhqQ12Ilo7nyTlObMxSLci/ijo2dVD+fn7RPx/A09kFyee1dt5M/Yby/6IbrMr4n+aPnza9DSTxqYfNURpwZWHFR6TE6VA3OaqDWAdB04t89/1O/w1cDnyilFU='
channel_secret = '8ca4d5cc38858c4ee059f804550c3b4a'


def linebot(request):
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(channel_secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        reply_token = json_data['events'][0]['replyToken']
        process_message(json_data, reply_token)
        return 'OK'
    except Exception as e:
        logging.error(f'Error processing the request: {e}', exc_info=True)
        return 'Error', 500

def process_message(json_data, reply_token):
    try:
        if 'message' in json_data['events'][0]:
            message = json_data['events'][0]['message']
            if message['type'] == 'text':
                handle_text_message(message, reply_token)
    except Exception as e:
        logging.error(f'Error processing message: {e}', exc_info=True)
        raise

def handle_text_message(message, reply_token):
    try:
        text = message['text']
        if text.startswith('bike'):
            station_name = text.split(' ', 1)[1] if len(text.split(' ', 1)) > 1 else None
            if station_name:
                get_bike_info_msg = bike_info(station_name)
                reply_message(get_bike_info_msg, reply_token, access_token)
            else:
                reply_message("請輸入完整的站名，例如：'bike 文心森林公園'", reply_token, access_token)
        else:
            reply_message("若需要查詢自行車站點信息，請使用 'bike 站名' 的格式，例如：'bike 文心森林公園'", reply_token, access_token)
    except Exception as e:
        logging.error(f'Error handling text message: {e}', exc_info=True)
        raise

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

def reply_message(msg, rk, token):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = {
        'replyToken': rk,
        'messages': [{
            "type": "text",
            "text": msg
        }]
    }
    response = requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, data=json.dumps(body).encode('utf-8'))
    if response.status_code != 200:
        logging.error(f'Failed to send reply: {response.status_code} {response.text}')
    return response


