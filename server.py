# server.py
import asyncio
import warnings
import os

# خاموش کردن SyntaxWarning های مرتبط با jdatetime که تو لاگ مزاحمت ایجاد می‌کنه
warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

# از اینجا به بعد سرور وب و اجرای همزمان بات
from flask import Flask
import nest_asyncio
import test2  # فایل بات شما (همون test2.py که فرستادی)

nest_asyncio.apply()  # ضروری برای محیط‌هایی مثل Render

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

async def run_flask():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    # Render معمولاً PORT را در env می‌فرسته؛ اگر نبود از 10000 استفاده کن
    port = int(os.environ.get("PORT", 10000))
    config.bind = [f"0.0.0.0:{port}"]
    await serve(app_web, config)

# self-ping برای جلوگیری از sleep شدن سرویس (در صورت نیاز)
async def self_ping():
    import aiohttp
    # سرویس خودت رو بزن؛ اگر Render URL رو داری، بذارش اینجا.
    base = os.environ.get("SELF_PING_URL")  # مثلاً https://your-service.onrender.com
    if not base:
        return  # اگر URL ندادی، پینگ فعال نمیشه
    # همیشه سعی کن کمتر از 4 دقیقه بذاری (Render معمولا 15 دقیقه تا خواب)
    interval = int(os.environ.get("SELF_PING_INTERVAL", 240))
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(base, timeout=10)
            except Exception:
                # نادیده گرفتن خطا (ممکنه گاهی جواب نده)
                pass
            await asyncio.sleep(interval)

async def main():
    # ایجاد تسک‌ها بدون nested run / run_until_complete
    bot_task = asyncio.create_task(test2.main())
    flask_task = asyncio.create_task(run_flask())

    # اگر SELF_PING_URL ست شده، پینگ داخلی هم اجرا می‌کنیم تا سرویس نخوابه
    ping_task = None
    if os.environ.get("SELF_PING_URL"):
        ping_task = asyncio.create_task(self_ping())
        await asyncio.gather(bot_task, flask_task, ping_task)
    else:
        await asyncio.gather(bot_task, flask_task)

if __name__ == "__main__":
    # اگر Render از Python 3.13 استفاده می‌کنه و خطا دیدی، به runtime (see note) برگردون 3.11.8
    asyncio.run(main())