import asyncio
import warnings
import os
from flask import Flask
from hypercorn.asyncio import serve
from hypercorn.config import Config
import nest_asyncio

# نام فایل بات رو اینجا ایمپورت کن (من فرض کردم اسم فایلت test2.py هست)
import test2 

# نادیده گرفتن وارنینگ‌های jdatetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

nest_asyncio.apply()

app_web = Flask(__name__)  # اصلاح شد: __name__

@app_web.route("/")
def home():
    return "Bot is alive and running!"

async def run_flask():
    config = Config()
    # دریافت پورت از رندر
    port = int(os.environ.get("PORT", 10000))
    config.bind = [f"0.0.0.0:{port}"]
    await serve(app_web, config)

async def self_ping():
    import aiohttp
    base = os.environ.get("SELF_PING_URL")
    if not base:
        return
    
    interval = int(os.environ.get("SELF_PING_INTERVAL", 240))
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(base, timeout=10)
            except Exception:
                pass
            await asyncio.sleep(interval)

async def main():
    # تسک‌های همزمان
    # مهم: بات رو صدا می‌زنیم اما مدیریت سیگنال رو ازش می‌گیریم
    bot_task = asyncio.create_task(test2.main())
    flask_task = asyncio.create_task(run_flask())
    
    tasks = [bot_task, flask_task]
    
    if os.environ.get("SELF_PING_URL"):
        ping_task = asyncio.create_task(self_ping())
        tasks.append(ping_task)
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":  # اصلاح شد: __name__
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
