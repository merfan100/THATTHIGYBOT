from flask import Flask
import threading
import app  # این همون فایل بات تلگرام تو هست

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

# اجرای ربات تلگرام در یک Thread جدا
def run_bot():
    import app  # همین فایل بات تلگرام تو
    # app.py خودش polling داره، اجرا میشه

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",10000))
    app_web.run(host="0.0.0.0", port=port)
