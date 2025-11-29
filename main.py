import os
import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ------------------------- تنظیمات ثابت -------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))

SUPPORT_USERNAME = "MahdeKoodakSupport"
CHANNEL_USERNAME = "bigkidkindergarten"
CARD_NUMBER = "6219861815202733"
CARD_OWNER = "ثمین دهقانی"

registration_status = {
    "esfahan": False,
    "tehran": False,
    "shiraz": False,
}

# ------------------------- پیام‌های آماده -------------------------

CLOSED_EVENT_MESSAGE = (
    "سلام🌱\n\n"
    "خوشحالیم که مشتاق حضور در جمع مهدکودک‌بزرگترها هستید\n\n"
    "در حال حاضر، در شهر انتخابیتون سانس فعالی برای ثبت‌نام نداریم و می‌تونید از طریق "
    "کانال تلگراممون از سانس‌های جدیدی که گذاشته میشه باخبر بشید✨️"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅 زمان:\nجمعه، 23 آبان 1404\nساعت 17 الی 20\n\n"
    "📍 مکان:\nباغچه کودکی هم‌صدا\n\n"
    "☁️ هزینه: 590 هزارتومان\n\n"
    "🔸 شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گی‌رید.\n\n"
    "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

ESFAHAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها اصفهان\n\n"
    "👫مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅زمان:\n"
    "پنجشنبه، ۱۳ آذرماه ۱۴۰۴\n"
    "ساعت 17 الی 20\n\n"
    "📍مکان:\n"
    "مهدکودک خلاقان کوچک ، میرزاطاهر\n\n"
    "☁️ هزینه: ۴۵۰ هزارتومان\n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گی‌رید.\n\n"
    "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

TEHRAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 590 هزارتومان
دونفر : 1,121 هزارتومان
سه نفر: 1,652 هزارتومان
چهار نفر: 2,183 هزارتومان
پنج نفر: 2,741 هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

ESFAHAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : ۴۵۰ هزارتومان
دونفر : ۸۵۵ هزارتومان
سه نفر: ۱,۲۶۰ هزارتومان
چهار نفر: ۱,۶۶۵ هزارتومان
پنج نفر: ۲،۰۷۰ هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

GLOBAL_CONFIRM_MESSAGE = (
    "پرداخت شما تأیید شد 🌱\n"
    "ثبت‌نامتون در رویداد مهدکودک‌بزرگترها کامل شد✅\n\n"
    "اطلاعات تکمیلی رویداد،‌ یک روز قبل از اون براتون ارسال میشه✨\n\n"
    "منتظرتون هستیم 💛"
)

# ------------------------- توابع کمکی -------------------------

def support_back(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        ]
    )


def support_only_links() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
    )


# ------------------------- /start -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ شهرتو انتخاب کن", callback_data="choose_city")],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
    ]

    if update.effective_user and update.effective_user.id == ADMIN_CHAT_ID:
        for city in ["esfahan", "tehran", "shiraz"]:
            keyboard.append([
                InlineKeyboardButton(f"🔒 بستن {city}", callback_data=f"close_{city}"),
                InlineKeyboardButton(f"🔓 باز کردن {city}", callback_data=f"open_{city}"),
            ])

    greeting = (
        "سلام 🌱\n"
        "خوشحالم که می‌خواین بیاین تا برای چند لحظه زندگی روزمره رو متوقف کنیم 🥰"
    )

    if update.message:
        await update.message.reply_text(greeting, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=InlineKeyboardMarkup(keyboard))


# ------------------------- هندلر دکمه‌ها -------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "choose_city":
        def status(city):
            return "✅" if registration_status.get(city, False) else "❌"

        keyboard = [
            [InlineKeyboardButton(f"{status('esfahan')} اصفهان", callback_data="city_esfahan")],
            [InlineKeyboardButton(f"{status('tehran')} تهران", callback_data="city_tehran")],
            [InlineKeyboardButton(f"{status('shiraz')} شیراز", callback_data="city_shiraz")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
        await query.edit_message_text("✨ کدوم شهر رو میخوای شرکت کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "city_esfahan":
        if registration_status["esfahan"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="pay_esfahan")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("بازگشت", callback_data="choose_city")],
            ]
            await query.edit_message_text(ESFAHAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back("choose_city"))

    elif query.data == "city_tehran":
        if registration_status["tehran"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="pay_tehran")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("بازگشت", callback_data="choose_city")],
            ]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back("choose_city"))

    elif query.data == "city_shiraz":
        if registration_status["shiraz"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="pay_shiraz")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("بازگشت", callback_data="choose_city")],
            ]
            await query.edit_message_text("مهدکودک‌بزرگترها شیراز ✨", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back("choose_city"))

    elif query.data == "pay_tehran":
        context.user_data["city"] = "tehran"
        await query.edit_message_text(TEHRAN_RECEIPT_MESSAGE, reply_markup=support_back("choose_city"))

    elif query.data == "pay_esfahan":
        context.user_data["city"] = "esfahan"
        await query.edit_message_text(ESFAHAN_RECEIPT_MESSAGE, reply_markup=support_back("choose_city"))

    elif query.data == "pay_shiraz":
        context.user_data["city"] = "shiraz"
        await query.edit_message_text(
            "لطفاً مبلغ را واریز کرده و فیش را به همراه نام و شماره تماس ارسال کنید.\n\n🔜 جزئیات به زودی",
            reply_markup=support_back("choose_city")
        )

    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(f"ثبت‌نام برای {city} {state}", reply_markup=support_back("start"))

    elif query.data.startswith("confirm_"):
        parts = query.data.split("_")
        if len(parts) >= 2:
            user_id = int(parts[1])
        else:
            return
        await context.bot.send_message(chat_id=user_id, text=GLOBAL_CONFIRM_MESSAGE)
        msg = query.message
        cap = msg.caption or ""
        date = jdatetime.date.today().strftime("%Y/%m/%d")
        new_cap = f"{cap}\n\n✅ تایید شده در تاریخ {date}"
        await query.edit_message_caption(caption=new_cap, reply_markup=None)

    elif query.data.startswith("reject_info_") or query.data.startswith("reject_amount_") or query.data.startswith("reject_"):
        parts = query.data.split("_")
        if len(parts) >= 3:
            user_id = int(parts[-1])
        elif len(parts) == 2:
            user_id = int(parts[1])
        else:
            return

        if "info" in query.data:
            text = (
                "ثبت‌نام شما به دلیل اطلاعات ناقص رد شد🥲\n"
                "لطفاً فیش رو دوباره ارسال کنید و نام و نام خانوادگی خودتون به همراه شماره تماستون را "
                "در کپشن فیش بنویسید 🌱"
            )
        else:
            text = (
                f"فیش واریزی شما رد شد❌\n"
                f"مبلغ پرداختی با مبلغ تعیین شده همخوانی نداشت.\n"
                f"برای اطلاعات بیشتر به پشتیبانی به آیدی @{SUPPORT_USERNAME} پیام دهید"
            )

        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=support_back("choose_city"))

        msg = query.message
        cap = msg.caption or ""
        date = jdatetime.date.today().strftime("%Y/%m/%d")
        reason_text = "اطلاعات ناقص" if "info" in query.data else "مبلغ اشتباه"
        new_cap = f"{cap}\n\n❌ رد شده ({reason_text}) در تاریخ {date}"
        await query.edit_message_caption(caption=new_cap, reply_markup=None)


# ------------------------- دریافت عکس فیش -------------------------

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city")
    if not city or not registration_status.get(city):
        await update.message.reply_text(
            "❌ لطفاً ابتدا از مسیر «نهایی کردن ثبت‌نام» وارد شوید و سپس فیش را ارسال کنید.",
            reply_markup=support_back("choose_city"),
        )
        return

    photo = update.message.photo[-1]
    caption = update.message.caption or "بدون کپشن"
    user = update.message.from_user
    user_id = user.id
    admin_caption = f"از طرف {user.full_name} (@{user.username or 'بدون نام‌کاربری'})\n\nکپشن:\n{caption}"

    confirm_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأیید ثبت‌نام", callback_data=f"confirm_{user_id}")],
        [InlineKeyboardButton("❌ رد - اطلاعات ناقص", callback_data=f"reject_info_{user_id}")],
        [InlineKeyboardButton("❌ رد - مبلغ اشتباه", callback_data=f"reject_amount_{user_id}")],
    ])

    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption=admin_caption, reply_markup=confirm_buttons)
    await update.message.reply_text(
        "فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی توسط تیم هستیم و نتیجه را اطلاع می‌دهیم 🌱",
        reply_markup=support_back("choose_city"),
    )


# ------------------------- اجرای ربات -------------------------

async def set_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع")])


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN ست نشده")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_commands).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()