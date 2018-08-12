from flask import Flask, request, abort
import os

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

channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def make_image_messages():
    messages = ImageSendMessage(
        original_content_url="https://photos.app.goo.gl/WYo6BPrSGHjewsd78", #JPEG 最大画像サイズ：240×240 最大ファイルサイズ：1MB(注意:仕様が変わっていた)
        #preview_image_url="shorthand-chart.jpg" #JPEG 最大画像サイズ：1024×1024 最大ファイルサイズ：1MB(注意:仕様が変わっていた)
    )
    return messages

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
    if event.message.text == '表くれ':
        
        messages = make_image_messages()
        line_bot_api.reply_message(
            event.reply_token,
            messages)

    else:
        q = poker_chart.main() #type(q)==tuple

        profile = line_bot_api.get_profile(event.source.user_id)

        print(profile.display_name)
        print(profile.user_id)
        print(profile.picture_url)
        print(profile.status_message)
        text = '{user_name}\n{question}'.format(user_name=profile.display_name, question=q[0])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()