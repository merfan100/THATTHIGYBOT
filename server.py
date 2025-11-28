# --- تنظیمات سرور وب برای اجرای بات تلگرام در حالت Webhook ---
import asyncio
import warnings
import os
import traceback

from flask import Flask, request, jsonify
from hypercorn.asyncio import serve
from hypercorn.config import Config

from telegram import Update
import test2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="jdatetime")

app_web = Flask(__name__)
telegram_app = None

# ------------------------- روت‌های سرور وب -------------------------

@app_web.route("/")
def home():
    return "Bot is alive and running!"

@app_web.route("/telegram", methods=["POST"])
def telegram_webhook():
    global telegram_app

    if not telegram_app:
        print("❌ Bot not initialized when Webhook received an update.")
        return jsonify({"status": "error", "message": "Bot not initialized"}), 503

    try:
        data = request.get_json(force=True)
        user_id = data.get('message', {}).get('from', {}).get('id', 'N/A')
        print(f"✅ Webhook received update. User ID: {user_id}")

        update = Update.de_json(data, telegram_app.bot)
        loop = asyncio.get_event_loop()

        asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update), loop
        ).result()

        print(f"✅ Update for User {user_id} processed successfully.")
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Error processing update: {e}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 200

# ------------------------- توابع راه‌اندازی سرور -------------------------

async def run_flask():
    config = Config()
    # Render همیشه PORT رو به صورت متغیر محیطی می‌فرسته
    port = int(os.environ["PORT"])  # اجباری می‌کنیم که PORT وجود داشته باشه
    config.bind = [f"0.0.0.0:{port}"]
    print(f"🔥 Starting web server on port: {port} 🔥")
    await serve(app_web, config)

async def self_ping():
    import aiohttp
    base = os.environ.get("SELF_PING_URL")
    if not base:
        print("💖 Self-ping URL not set. Skipping self-ping task.")
        return

    interval = int(os.environ.get("SELF_PING_INTERVAL", 240))
    print(f"💖 Self-ping activated every {interval} seconds to {base}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(base, timeout=10)
            except Exception as e:
                print(f"Self-ping failed: {e}")
            await asyncio.sleep(interval)

async def main():
    print("🚀 Main server function started. Initializing bot... 🚀")
    global telegram_app

    print(f"BOT_TOKEN set: {'✅ Yes' if os.environ.get('BOT_TOKEN') else '❌ No'}")
    print(f"WEBHOOK_URL set: {'✅ Yes' if os.environ.get('WEBHOOK_URL') else '❌ No'}")

    telegram_app = await test2.main()

    if telegram_app is None:
        print("❌ Bot application initialization failed. Server cannot run.")
        return

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
        print(f"An unexpected fatal error occurred: {e}")
