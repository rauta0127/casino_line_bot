from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
import os
import time
import datetime
import sys

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
    status = db.Column(db.String(10), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)
    user_name = db.Column(db.String(30), nullable=True)
    latest_message = db.Column(db.String(100), nullable=True)
    game = db.Column(db.String(10))
    poker_handclass = db.Column(db.String(5))
    poker_position = db.Column(db.String(10))
    poker_status = db.Column(db.String(20))
    poker_action = db.Column(db.String(2))

    def __init__(self, user_id, status, updated_at, user_name, latest_message):
        self.user_id = user_id
        self.status = status
        self.updated_at = updated_at
        self.user_name = user_name
        self.latest_message = latest_message

def createUser(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user_id = db.session.query(Users.user_id).all()
    if len(user_id) == 0:
        new_user = Users(
                    user_id=profile.user_id,
                    status='ready', 
                    updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    user_name=profile.display_name, 
                    latest_message=event.message.text,
                )
        db.session.add(new_user)
        db.session.commit()
        text = '{}さん, はじめまして！ルール説明は私の投稿ページを見てください！'.format(profile.display_name)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
        sys.exit(1)
    else:
        if not (event.source.user_id in list(user_id[0])):
            new_user = Users(
                    user_id=profile.user_id,
                    status='ready', 
                    updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    user_name=profile.display_name, 
                    latest_message=event.message.text,
                    )
            db.session.add(new_user)
            db.session.commit()

            text = '{}さん, はじめまして！ルール説明は私の投稿ページを見てください！'.format(profile.display_name)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
            sys.exit(1)




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
    # Create User row
    # createUser(event)
    #user = Users(profile.user_id, 'ready', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), profile.display_name, event.message.text)
    #db.session.add(user)
    #db.session.commit()

    user_status = db.session.query(Users).filter(Users.user_id==profile.user_id).first().status

    if user_status == 'ready':
        if event.message.text == '表くれ':
            questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            questioned_user.latest_message=event.message.text
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=chart_jpg_url, 
                    preview_image_url=chart_jpg_url
                ))

        elif event.message.text == 'エントリー':
            hand_class, position, status, question, answer = poker_chart.main()
            questioned_user = db.session.query(Users).filter(Users.user_id==profile.user_id).first()
            questioned_user.status='questioned' 
            questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            questioned_user.latest_message=event.message.text
            questioned_user.game='poker'
            questioned_user.poker_handclass=hand_class
            questioned_user.poker_position=position
            questioned_user.poker_status=status
            questioned_user.poker_action=answer
            db.session.commit()
            text = '{user_name}さん\n{question}'.format(user_name=profile.display_name, question=question)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
        else:
            text = 'エントリーしますか？'
            questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            questioned_user.latest_message=event.message.text
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))

    if user_status == 'questioned':
        questioned_user = db.session.query(Users).filter(Users.user_id==profile.user_id).first()
        if event.message.text == '表くれ':
            text = '今はダメです！'
            questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            questioned_user.latest_message=event.message.text
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
        elif event.message.text in ['R', 'RF', 'C', 'C2', 'F']:
            correct_answer = questioned_user.poker_action
            if correct_answer == event.message.text:
                text = '正解です！'
                questioned_user.status='ready'
                questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                questioned_user.latest_message=event.message.text
                db.session.commit()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
            else:
                text = '違います！'
                questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                questioned_user.latest_message=event.message.text
                db.session.commit()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
        else:
            text = 'R, RF, C, C2, Fで答えてください！'
            questioned_user.updated_at=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            questioned_user.latest_message=event.message.text
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()