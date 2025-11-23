import asyncio
from flask import Flask
import test2  # فایل بات تلگرام تو
import nest_asyncio

nest_asyncio.apply()  # مهم برای Render که خودش event loop داره

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

async def run_flask():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]  # پورت Render
    await serve(app_web, config)

async def main():
    # اجرای همزمان Flask و ربات
    await asyncio.gather(
        run_flask(),
        test2.main()  # فرض بر اینه که فایل بات تو تابع main داره
    )

if __name__ == "__main__":
    asyncio.run(main())