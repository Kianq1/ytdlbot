import os
import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8580077921:AAEW59TyYEnDQUp5vBdeQyOImyxQkeVgv9U"

user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا کیفیت رو انتخاب کنی.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # اگر لینک یوتیوب نبود → پیام بده
    if "youtube.com" not in text and "youtu.be" not in text:
        await update.message.reply_text("این لینک یوتیوب نیست. لطفاً یک لینک معتبر بفرست.")
        return

    # ذخیره لینک
    user_links[update.message.from_user.id] = text

    # ساخت دکمه‌های انتخاب کیفیت
    keyboard = [
    [
        InlineKeyboardButton("240p", callback_data="240"),
        InlineKeyboardButton("480p", callback_data="480"),
    ],
    [
        InlineKeyboardButton("720p", callback_data="720"),
        InlineKeyboardButton("1080p", callback_data="1080"),
    ],
    [
        InlineKeyboardButton("2K", callback_data="1440"),
        InlineKeyboardButton("4K", callback_data="2160"),
    ],
    [
        InlineKeyboardButton("8K", callback_data="4320"),
    ],
    [
        InlineKeyboardButton("☕ حمایت مالی", url="https://www.coffeebede.com/kianpoo11"),
    ],
    ]

    await update.message.reply_text(
        "کیفیت مورد نظر رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("لینک پیدا نشد. دوباره لینک بفرست.")
        return

    choice = query.data

    # انتخاب کیفیت بر اساس ارتفاع تصویر
    ydl_opts = {
        "format": f"bestvideo[height<={choice}]+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": "/tmp/video.mp4",
    }
    filename = "/tmp/video.mp4"

    await query.edit_message_text(f"در حال دانلود {choice}p ...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_video(open(filename, "rb"))

    except Exception as e:
        await query.message.reply_text(f"خطا در دانلود: {e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
