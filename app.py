from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('DLoGsTWCtTneRf8uaBT2yfJ6NB9MGqLR0ef1lFEl26kruAfjtmZazhJdAda2CQ/AluN+/1N1iMB0IP9Pj+Azv+OLt4aYkh2thAXQXnRZSQpS85n+75Ex6bIQDBefAjtFGG3pNMUx8g+rqhtlafOwiQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a59c48993083c003420593f6d05ebb27')

@app.route("/")
def hello_world():
    return "hello world!"

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()