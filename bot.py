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

# توکن رو اینجا بذار یا از متغیر محیطی استفاده کن
TOKEN = "7691303330:AAF6G85yQFJYq19yywyZ2UYMIJM7k6pP_bQ"

# این دیکشنری لینک هر کاربر رو نگه می‌داره
user_links = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا کیفیت رو انتخاب کنی.")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text.strip()

    # ذخیره لینک برای این کاربر
    user_links[user_id] = url

    # ساخت دکمه‌های انتخاب کیفیت
    keyboard = [
        [
            InlineKeyboardButton("🎬 360p", callback_data="video_360p"),
            InlineKeyboardButton("🎬 720p", callback_data="video_720p"),
        ],
        [
            InlineKeyboardButton("🎧 فقط صدا (MP3)", callback_data="audio_mp3"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "کیفیت مورد نظر رو انتخاب کن:", reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("لینک پیدا نشد. دوباره لینک یوتیوب رو بفرست.")
        return

    choice = query.data

    # ویدیو 360p
    if choice == "video_360p":
        await query.edit_message_text("در حال دانلود ویدیو با کیفیت 360p ...")
        ydl_opts = {
            "format": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "outtmpl": "video_360p.mp4",
            "merge_output_format": "mp4",
        }
        filename = "video_360p.mp4"
        send_type = "video"

    # ویدیو 720p
    elif choice == "video_720p":
        await query.edit_message_text("در حال دانلود ویدیو با کیفیت 720p ...")
        ydl_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "outtmpl": "video_720p.mp4",
            "merge_output_format": "mp4",
        }
        filename = "video_720p.mp4"
        send_type = "video"

    # فقط صدا (MP3)
    elif choice == "audio_mp3":
        await query.edit_message_text("در حال دانلود نسخه MP3 ...")
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

    else:
        await query.edit_message_text("انتخاب نامعتبر.")
        return

    try:
        # دانلود با yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ارسال فایل
        if send_type == "video":
            await query.message.reply_video(open(filename, "rb"))
        else:
            await query.message.reply_audio(open(filename, "rb"))

    except Exception as e:
        await query.message.reply_text(f"خطا در دانلود: {e}")
    finally:
        # حذف فایل بعد از ارسال
        if os.path.exists(filename):
            os.remove(filename)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
