import os
import schedule
import time
import threading
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi
from flask import Flask, request, Blueprint

# Replace with your own values
channel_secret = '3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU='
channel_access_token = '60c382a7a969d7c0a80e26d8c792d34f'

messaging_api = MessagingApi(channel_access_token)
handler = WebhookHandler(channel_secret)

reminders = {}

def send_reminder(event_id):
    reminder = reminders[event_id]
    messaging_api.push_message(reminder['user_id'], TextSendMessage(text=reminder['title']))

def add_reminder(user_id, title, time):
    event_id = str(len(reminders))
    reminders[event_id] = {
        'user_id': user_id,
        'title': title,
        'time': time,
    }
    schedule.every().day.at(time).do(send_reminder, event_id)

app = Flask(__name__)
app.secret_key = os.urandom(24)

webhook_bp = Blueprint('webhook_bp', __name__)

@webhook_bp.route('/callback', methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature. Please check your channelaccess token/channel secret.'
    except Exceptionas as e:
        app.logger.error('Error when handling webhook body: ' + str(e))
        return 'Internal server error'

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text.startswith('Add reminder'):
        title, time = text.split(' ', 1)[1].split(' ', 1)
        add_reminder(event.source.user_id, title, time)
        messaging_api.reply_message(event.reply_token, TextSendMessage(text='Reminder added.'))

if __name__ == '__main__':
    app.register_blueprint(webhook_bp)

    # Run the scheduler in a separate thread
    schedule_thread = threading.Thread(target=schedule.run_pending)
    schedule_thread.start()

    app.run()