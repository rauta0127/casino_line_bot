from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2
import time
import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)
from linebot.exceptions import LineBotApiError

import poker_chart

app = Flask(__name__)
db_uri = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

chart_jpg_url = 'https://lh3.googleusercontent.com/Q-uM4RpSIz6OdMQrOx4uyt7'\
                'RtS63NSjZ7Oe_LF5F556WfGvlArAo6fzIVz8Mn_PyhxxD9jjaBLGbZHTmw'\
                'SJD35fgzCZ-cHy9YoOR93MMQvJanvWl0RxS4e7aJqUdOenCqLYiERZW_b7j'\
                'TVeaMdc2oOawOvA9--uZCi50Fbu5hL0_BzaZZbnS3M6seOFsjSrCBFt932X1'\
                'SqKuqC9gBAcaD7g-yzOoTW_Meiy6lQoR1b3AqJ0UecZk7y0Q1p7O4Kcrq8iIL'\
                'Y4H-aGXqvVEXBYsUeleBNdhYju_StQntKM_Yz-SFsdL3jzT51VunjOvwKNUTWQ'\
                'Hbz6OyLNOKZ9ZeYY_yI0KEHS05SuDX6Kwa0rrhAdYjN9m9p_VetxbbgrZ2rNsvi'\
                'GSXPVZzGz2UTdT5dvXk1h8Ih9lQJuuNkSINa294PMK5nQYS1FSv4LBghqt6QK1fM'\
                'c79ODV5v3hPDvfBzxHVg7SJVEuCQqjyzHotOf5Aefw2Hdp0MGcoAd6PQntAn0Y76O'\
                'RN-CQM0s3gG30Q-ML2kACGfKh3RmEyDEYo7eP8Sq8lKZdAzl77sfUXHa8F9xe7gvl1'\
                'nZoZvsU-ehwysonxkkxHlb03kKQqfu_79jE8My1DK-vIVdiVz_5vP3ZSuU8c6mNVt4m'\
                'NwUMrqhGDOz4qclCnMqIcmyg=w610-h863-no'

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), unique=True, nullable=True)
    status = db.Column(db.String(10), unique=True, nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)

    def __init__(self, user_id, status, updated_at):
        self.user_id = user_id
        self.status = status
        self.updated_at = updated_at



def put_data4(dict):
    with conn:
        conn.execute('INSERT INTO casino_user VALUES (null, :user_id, :status)', dict)
    # conn.close()

def read_data():
    cur = cursor.execute('SELECT * FROM users')
    users = [user for user in cur.fetchall()]
    for i in users:
        print(i)
    cursor.close()


@app.route("/")
def index():
    return "This is LINE casino-bot app. Running!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    print(profile.display_name)
    print(profile.user_id)
    user = Users(profile.user_id, 'ready', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(user)
    db.session.commit()

    users = Users.query.all()
    print (users)

    if event.message.text == '表くれ':
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=chart_jpg_url, 
                preview_image_url=chart_jpg_url
            ))

    else:
        q = poker_chart.main() #type(q)==tuple
        text = '{user_name}\n{question}'.format(user_name=profile.display_name, question=q[0])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()