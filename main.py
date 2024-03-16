import json
import os
import time
import django
import datetime
import urllib.request
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
from flask import Flask, render_template
from linebot import LineBotApi, WebhookHandler

app = Flask(__name__)

# 設定 Line Bot 的 Channel Access Token 和 SpreadSheet ID
CHANNEL_ACCESS_TOKEN = "3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU="
SPREADSHEET_ID = "1Xx0TnoamQkH0_gaLOOzMyAmGBUwufYKGURHVxrzfOiw"
Channel_secret= "60c382a7a969d7c0a80e26d8c792d34f"

# 設定要忽略的字詞
IGNORE_WORDS = ["help", "?"]

# 設定停止提醒的關鍵字
STOP_ALARM_WORD = "ok"

# 取得試算表的資料
def get_sheet_data():
    spreadsheet = SpreadsheetApp.open_by_id(SPREADSHEET_ID)
    sheet = spreadsheet.getActiveSheet()
    last_row = sheet.getLastRow()
    last_column = sheet.getLastColumn()
    sheet_data = sheet.getSheetValues(1, 1, last_row, last_column)
    return sheet_data

# 處理使用者傳送的訊息
def handle_user_message(event):
    # 取得使用者 ID 和傳送的訊息
    user_id = event["source"]["userId"]
    message_text = event["message"]["text"]

    # 忽略指定的字詞
    if message_text.lower() in IGNORE_WORDS:
        return

    # 處理停止提醒的指令
    if message_text.lower() == STOP_ALARM_WORD.lower():
        stop_alarm()
        return

    # 取得使用者目前回答到第幾題
    answer_index, next_question_index = get_user_answer(user_id, message_text)

    # 如果使用者已經回答完所有問題，就設定提醒時間
    if next_question_index == 1:
        set_alarm(answer_index)
        return

    # 傳送下一題給使用者
    send_question(user_id, next_question_index)

# 取得使用者回答到第幾題
def get_user_answer(user_id, message_text):
    sheet_data = get_sheet_data()
    for i in range(2, len(sheet_data)):
        if sheet_data[i][0] == user_id and sheet_data[i][len(sheet_data[0]) - 1] == "":
            for j in range(1, len(sheet_data[0]) - 1):
                if sheet_data[i][j] == "":
                    break
            sheet_data[i][j] = message_text
            # 如果使用者已經回答完所有問題，就設定提醒時間
            if j + 3 == len(sheet_data[0]):
                return i, 0
            else:
                return i, j + 2
    return None, 1

# 設定提醒時間
def set_alarm(answer_index):
    sheet_data = get_sheet_data()
    alarm_time = datetime.datetime.strptime(sheet_data[answer_index][1] + " " + sheet_data[answer_index][2], "%Y/%m/%d %H:%M")
    # 使用者的提醒時間如果已經過了，就跳過設定提醒的步驟
    if alarm_time < datetime.datetime.now(timezone.utc+8):
        return
    # 設定提醒

def stop_alarm():
    sheet_data = get_sheet_data()
    for i in range(2, len(sheet_data)):
        if sheet_data[i][4] == 0:
            # 檢查提醒時間是否已經過了
            if alarm_time < datetime.datetime.now():
                alarm_time = datetime.datetime.strptime(sheet_data[i][1] + " " + sheet_data[i][2], "%Y/%m/%d %H:%M")
                # 取消提醒

def send_question(user_id, question_index):
    sheet_data = get_sheet_data()
    question = sheet_data[0][question_index - 1]
    # 如果是日期問題，就傳送日期選擇器
    if question_index == 2:
        send_date_picker(user_id, question)
    # 如果是時間問題，就傳送時間選擇器
    elif question_index == 3:
        send_time_picker(user_id, question)
    # 否則就傳送確認訊息
    else:
        send_confirm_message(user_id, question)

# 傳送日期選擇器
def send_date_picker(user_id, question):
    # 設定日期選擇器的參數
    data = {
        "type": "datetimepicker",
        "label": question,
        "data": "DateMessage",
        "mode": "date",
        "id": "date_picker",
    }
    # 傳送日期選擇器
    send_message(user_id, [data])

# 傳送時間選擇器
def send_time_picker(user_id, question):
    # 設定時間選擇器的參數
    data = {
        "type": "datetimepicker",
        "label": question,
        "data": "TimeMessage",
        "mode": "time",
        "id": "time_picker",
    }

    # 傳送時間選擇器
    send_message(user_id, [data])

# 傳送確認訊息
def send_confirm_message(user_id, question):
    # 設定確認訊息的參數
    actions = {
    {
        "type": "postback",
        "label": "確認",
        "data": "DecideConfirm",
        "text": "確認",
    },
    {
        "type": "postback",
        "label": "取消",
        "data": "DecideCancel",
        "text": "取消",
    },

    # 傳送確認訊息
    send_message(user_id, [data])}

# 傳送訊息
def send_message(user_id, messages):
    # 設定傳送訊息的參數
    headers = {
        "Authorization": "Bearer " + CHANNEL_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    body = {
        "to": user_id,
        "messages": messages,
    }

    # 傳送訊息
    urllib.request.urlopen(
        "https://api.line.me/v2/bot/message/push",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
    )

@app.route('/callback', methods=['POST'])
def callback():
    # 驗證請求
    if request.headers['X-Line-Signature'] != 'YOUR_LINE_BOT_CHANNEL_SECRET':
        return '403 Forbidden', 403

    # 解析請求
    events = request.json['events']

    # 處理事件
    for event in events:
        if event['type'] == 'message':
            # 回覆訊息
            reply_message = {
                'type': 'text',
                'text': event['message']['text']
            }
            client.reply_message(event['replyToken'], reply_message)

    return '200 OK', 200
    
                            
if __name__ == "__main__":
      app.run()