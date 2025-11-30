from google import genai 
from google.genai import types
import os 
from dotenv import load_dotenv 
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent


# .env file 
load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# run app 
app = Flask(__name__)

# connect to line 
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# line 
@app.route("/ayame", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("簽名錯誤！")
        abort(400)

    return 'OK'

# api setting 
client = genai.Client(api_key=GEMINI_API_KEY)


# ai setting 
safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"  
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]
instruction = """

"""

# ai 
def Ayame(AI_input):
    answer = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=1.2,
            safety_settings=safe,
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
        contents=AI_input
    )
    return answer.text


# line and ai input message 
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 這裡也要用 v3 的方式來建立 API 客戶端喔！
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 讀取對方傳來的文字
        user_message = event.message.text
        AI_reply = Ayame(user_message)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=AI_reply)]
            )
        )

if __name__ == "__main__":
    app.run(port=5000)