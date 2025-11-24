# --- فایل server.py (کد نهایی و دیباگ شده) ---

import asyncio
import warnings
import os
from flask import Flask, request, jsonify 
from hypercorn.asyncio import serve
from hypercorn.config import Config
# nest_asyncio حذف شد
from telegram import Update 
# ایمپورت فایل بات
import test2 

# نادیده گرفتن وارنینگ‌های jdatetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

# nest_asyncio.apply() 👈 حذف شد

app_web = Flask(__name__)
telegram_app = None 

# ------------------------- روت‌های سرور وب -------------------------

@app_web.route("/")
def home():
    """روت ساده برای بررسی سلامت سرور."""
    return "Bot is alive and running!"

@app_web.route("/telegram", methods=["POST"])
async def telegram_webhook():
    """روت Webhook که آپدیت‌ها را از تلگرام دریافت می‌کند."""
    global telegram_app

    if not telegram_app:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 503

    try:
        data = request.get_json(force=True)
        # استفاده از Update.de_json
        update = Update.de_json(data, telegram_app.bot)
        
        # پردازش آپدیت
        await telegram_app.process_update(update)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
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
        return # اگر بات اجرا نشد، سرور هم اجرا نشود

    # ۲. تسک‌های همزمان: سرور وب و پینگ 
    flask_task = asyncio.create_task(run_flask())
    tasks = [flask_task]

    if os.environ.get("SELF_PING_URL"):
        ping_task = asyncio.create_task(self_ping())
        tasks.append(ping_task)
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        # استفاده مستقیم از asyncio.run 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Server stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
