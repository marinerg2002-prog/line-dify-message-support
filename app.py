import os

import requests
from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent


# .envファイルを読み込む
load_dotenv()

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = os.getenv("DIFY_API_URL")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 必須設定が入っているか確認
required_values = {
    "DIFY_API_KEY": DIFY_API_KEY,
    "DIFY_API_URL": DIFY_API_URL,
    "LINE_CHANNEL_SECRET": LINE_CHANNEL_SECRET,
    "LINE_CHANNEL_ACCESS_TOKEN": LINE_CHANNEL_ACCESS_TOKEN,
}

missing_values = [
    name for name, value in required_values.items() if not value
]

if missing_values:
    raise RuntimeError(
        "次の環境変数が設定されていません: "
        + ", ".join(missing_values)
    )


app = Flask(__name__)

configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/", methods=["GET"])
def health_check():
    return "LINE Dify Message Support is running.", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")

    if not signature:
        abort(400)

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200


@handler.add(
    MessageEvent,
    message=TextMessageContent,
)
def handle_message(event):
    user_message = event.message.text

    try:
        dify_answer = ask_dify(
            message=user_message,
            user_id=event.source.user_id,
        )
    except Exception as error:
        print(f"Dify API error: {error}")
        dify_answer = (
            "申し訳ありません。現在、文章を作成できませんでした。"
            "少し時間を置いて、もう一度お試しください。"
        )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=dify_answer)
                ],
            )
        )


def ask_dify(message: str, user_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "inputs": {},
        "query": message,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": user_id,
    }

    response = requests.post(
        DIFY_API_URL,
        headers=headers,
        json=data,
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()
    answer = result.get("answer")

    if not answer:
        raise ValueError(
            "Difyから回答が返りませんでした。"
        )

    return answer


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )