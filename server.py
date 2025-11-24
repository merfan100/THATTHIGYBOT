# --- فایل server.py (کد نهایی و اصلاح‌شده برای رفع خطای Flask Async) ---

import asyncio
import warnings
import os
# ایمپورت‌های ضروری برای سرور وب و تلگرام
from flask import Flask, request, jsonify 
from hypercorn.asyncio import serve
from hypercorn.config import Config
from telegram import Update 
# ایمپورت فایل بات
import test2 

# نادیده گرفتن وارنینگ‌های jdatetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

app_web = Flask(__name__)
telegram_app = None 

# ------------------------- روت‌های سرور وب -------------------------

@app_web.route("/")
def home():
    """روت ساده برای بررسی سلامت سرور."""
    return "Bot is alive and running!"

@app_web.route("/telegram", methods=["POST"])
def telegram_webhook(): 
    """
    روت Webhook که آپدیت‌ها را از تلگرام دریافت می‌کند.
    این تابع باید همگام (def عادی) باشد تا Flask دچار خطا نشود.
    """
    global telegram_app

    if not telegram_app:
        print("❌ Bot not initialized when Webhook received an update.")
        # اگر بات هنوز راه‌اندازی نشده، خطای 503 برمی‌گرداند.
        return jsonify({"status": "error", "message": "Bot not initialized"}), 503

    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        
        # 💡 راه‌حل رفع خطا:
        # ۱. گرفتن حلقه رویداد (Event Loop) اصلی که Hypercorn روی آن اجرا می‌شود.
        loop = asyncio.get_event_loop()
        
        # ۲. ارسال وظیفه ناهمزمان (process_update) به حلقه اصلی
        # .result() باعث می‌شود این تابع همگام صبر کند تا پردازش بات تمام شود.
        asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update), loop
        ).result() 

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        # در صورت بروز خطا در پردازش، همچنان کد 200 را برمی‌گردانیم تا تلگرام مجدداً آپدیت را ارسال نکند.
        print(f"Error processing update: {e}")
        return jsonify({"status": "error", "message": str(e)}), 200 

# ------------------------- توابع راه‌اندازی همزمان -------------------------

async def run_flask():
    """راه‌اندازی سرور Flask با Hypercorn."""
    config = Config()
    port = int(os.environ.get("PORT", 10000))
    config.bind = [f"0.0.0.0:{port}"]
    # ⭐️ پیام دیباگ ⭐️
    print(f"🔥 Attempting to bind web server to port: {port} 🔥") 
    await serve(app_web, config)

async def self_ping():
    """ارسال پینگ داخلی برای جلوگیری از خواب رفتن سرور."""
    import aiohttp
    base = os.environ.get("SELF_PING_URL")
    if not base:
        return

    interval = int(os.environ.get("SELF_PING_INTERVAL", 240))
    print(f"💖 Self-ping activated every {interval} seconds to {base}")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(base, timeout=10)
            except Exception:
                pass
            await asyncio.sleep(interval)

async def main():
    """وظایف اصلی: راه‌اندازی بات و سرور وب به صورت همزمان."""
    # ⭐️ پیام دیباگ ⭐️
    print("🚀 Main server function started. 🚀") 
    global telegram_app 

    # ۱. راه‌اندازی بات و دریافت نمونه Application 
    telegram_app = await test2.main() 

    if telegram_app is None:
        print("❌ Bot application initialization failed. Server cannot run.")
        return 

    # ۲. تسک‌های همزمان: سرور وب و پینگ 
    flask_task = asyncio.create_task(run_flask())
    tasks = [flask_task]

    if os.environ.get("SELF_PING_URL"):
        ping_task = asyncio.create_task(self_ping())
        tasks.append(ping_task)
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Server stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
