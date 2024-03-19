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
import re

# Replace with your own values
channel_secret = 'E5Lk6496pW037iX1ex33ev6r9763bVnp+ew+mnhMdX9zDx8yQjJjd6n6V71bOJeqa6VJqd36Jh4oQRLxjXRGqPYr594iNTJajeR29EM/c39arc0P0mbMTC4E9Ggr1+JhIwynSC2nLFCiyHFkgiaAggdB04t89/1O/w1cDnyilFU='
channel_access_token = '316f59aed7e9c194906f48bce4239b7f'

messaging_api = MessagingApi(channel_access_token)
handler = WebhookHandler(channel_secret)
reminders_lock = threading.Lock()
reminders = {}

def send_reminder(event_id):
    with reminders_lock:
        reminder = reminders[event_id]
        messaging_api.push_message(reminder['user_id'], TextSendMessage(text=reminder['title']))
        del reminders[event_id]

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
    except Exception as e:
        app.logger.error('Error when handling webhook body: ' + str(e))
        return 'Internal server error'

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    match = re.match(r'^Add reminder (.+) at (.+)$', text)
    if match:
        title, time = match.groups()
        add_reminder(event.source.user_id, title, time)
        messaging_api.reply_message(event.reply_token, TextSendMessage(text='Reminder added.'))

if __name__ == '__main__':
    app.register_blueprint(webhook_bp)

    # Run the scheduler in a separate thread
    schedule_thread = threading.Thread(target=schedule.run_pending)
    schedule_thread.start()

    app.run(host='0.0.0.0', port=80)