import os
import asyncio
from telegram.ext import Application, CommandHandler

# گرفتن توکن از متغیر محیطی
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("سلام! ربات ساده با polling بالا اومده ✅")

async def main():
    # ساخت اپلیکیشن تلگرام
    app = Application.builder().token(BOT_TOKEN).build()

    # اضافه کردن یک دستور ساده
    app.add_handler(CommandHandler("start", start))

    # شروع polling
    print("🚀 Bot started with polling...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
