from flask import Flask
import threading
import test2  # فایل بات تلگرام تو

import os

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

# اجرای ربات تلگرام در یک Thread جدا
def run_bot():
    import test2  # همین فایل بات تلگرام
    import asyncio
    asyncio.run(test2.main())  # فرض بر اینه که فایل بات تو تابع main داره

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)