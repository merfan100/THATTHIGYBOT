# --- فایل server.py (کد نهایی برای Webhook) ---

import asyncio
import warnings
import os
# request و jsonify برای هندل کردن آپدیت‌های تلگرام نیاز هستند
from flask import Flask, request, jsonify 
from hypercorn.asyncio import serve
from hypercorn.config import Config
import nest_asyncio
# کلاس Update از telegram برای پردازش به‌روزرسانی‌ها نیاز است
from telegram import Update

# نام فایل بات رو اینجا ایمپورت کن
# فرض بر این است که فایل بات شما 'test2.py' نام دارد
import test2 

# نادیده گرفتن وارنینگ‌های jdatetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

# اعمال nest_asyncio برای اجرای asyncio در محیطی مثل Flask
nest_asyncio.apply()

app_web = Flask(__name__)
# تعریف متغیر گلوبال برای نگهداری نمونه Application بات
telegram_app = None 

# ------------------------- روت‌های سرور وب -------------------------

@app_web.route("/")
def home():
    """روت ساده برای بررسی سلامت سرور."""
    return "Bot is alive and running!"

@app_web.route("/telegram", methods=["POST"])
async def telegram_webhook():
    """
    روت Webhook که آپدیت‌های POST از تلگرام را دریافت کرده 
    و آن‌ها را به هندلرهای بات (telegram_app) ارسال می‌کند.
    """
    global telegram_app
    
    # اطمینان از راه‌اندازی بات
    if not telegram_app:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 503
    
    # دریافت داده‌های JSON از تلگرام
    try:
        data = request.get_json(force=True)
        # تبدیل JSON دریافتی به شیء Update کتابخانه python-telegram-bot
        update = Update.de_json(data, telegram_app.bot)
        
        # پردازش آپدیت توسط بات
        await telegram_app.process_update(update)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error processing update: {e}")
        # در صورت خطا، باید به تلگرام OK داد تا از ارسال مجدد پیام جلوگیری شود
        return jsonify({"status": "error", "message": str(e)}), 200 

# ------------------------- توابع راه‌اندازی همزمان -------------------------

async def run_flask():
    """راه‌اندازی سرور Flask با Hypercorn برای اجرای ناهمزمان."""
    config = Config()
    # دریافت پورت از متغیر محیطی (مهم برای سرویس‌هایی مثل Render)
    port = int(os.environ.get("PORT", 10000))
    config.bind = [f"0.0.0.0:{port}"]
    print(f"🌐 Web server running on 0.0.0.0:{port}")
    await serve(app_web, config)

async def self_ping():
    """ارسال پینگ داخلی برای جلوگیری از خواب رفتن سرور (Idle Sleep)."""
    import aiohttp
    base = os.environ.get("SELF_PING_URL")
    if not base:
        return

    interval = int(os.environ.get("SELF_PING_INTERVAL", 240))
    print(f"💖 Self-ping activated every {interval} seconds to {base}")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # پینگ روت اصلی سرور (/)
                await session.get(base, timeout=10)
            except Exception as e:
                # این ارورها معمولاً فقط قطع موقت اتصال هستند و مهم نیستند
                pass
            await asyncio.sleep(interval)

async def main():
    """وظایف اصلی: راه‌اندازی بات و سرور وب به صورت همزمان."""
    global telegram_app 
    
    # ⭐️ ۱. راه‌اندازی بات و دریافت نمونه Application ⭐️
    telegram_app = await test2.main() 

    # ⭐️ ۲. تسک‌های همزمان: سرور وب و پینگ ⭐️
    flask_task = asyncio.create_task(run_flask())
    tasks = [flask_task]

    if os.environ.get("SELF_PING_URL"):
        ping_task = asyncio.create_task(self_ping())
        tasks.append(ping_task)
        
    # اجرای همه تسک‌ها به صورت موازی
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Server stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
