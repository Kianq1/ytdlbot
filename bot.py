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
            InlineKeyboardButton("🎬 360p", callback_data="360"),
            InlineKeyboardButton("🎬 720p", callback_data="720"),
        ],
        [
            InlineKeyboardButton("🎧 MP3", callback_data="mp3"),
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

    # انتخاب کیفیت
    if choice == "360":
        ydl_opts = {
            "format": "bestvideo[height<=360]+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
        }
        filename = "video.mp4"
        send_type = "video"
        await query.edit_message_text("در حال دانلود 360p ...")

    elif choice == "720":
        ydl_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
        }
        filename = "video.mp4"
        send_type = "video"
        await query.edit_message_text("در حال دانلود 720p ...")

    elif choice == "mp3":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.mp3",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        filename = "audio.mp3"
        send_type = "audio"
        await query.edit_message_text("در حال دانلود MP3 ...")

    else:
        await query.edit_message_text("انتخاب نامعتبر.")
        return

    # دانلود
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if send_type == "video":
            await query.message.reply_video(open(filename, "rb"))
        else:
            await query.message.reply_audio(open(filename, "rb"))

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
