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

TOKEN = os.getenv("8580077921:AAEW59TyYEnDQUp5vBdeQyOImyxQkeVgv9U")
user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا کیفیت رو انتخاب کنی.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # چک کردن لینک معتبر
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("این لینک یوتیوب نیست. لطفاً لینک معتبر بفرست.")
        return

    user_links[update.message.from_user.id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 360p", callback_data="video_360"),
            InlineKeyboardButton("🎬 720p", callback_data="video_720"),
        ],
        [
            InlineKeyboardButton("🎧 فقط صدا (MP3)", callback_data="audio_mp3"),
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

    if choice == "video_360":
        ydl_opts = {
            "format": "bestvideo[height<=360]+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
        }
        filename = "video.mp4"
        send_type = "video"
        await query.edit_message_text("در حال دانلود 360p ...")

    elif choice == "video_720":
        ydl_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
        }
        filename = "video.mp4"
        send_type = "video"
        await query.edit_message_text("در حال دانلود 720p ...")

    elif choice == "audio_mp3":
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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if send_type == "video":
            await query.message.reply_video(open(filename, "rb"))
        else:
            await query.message.reply_audio(open(filename, "rb"))

    except Exception as e:
        await query.message.reply_text(f"خطا: {e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
