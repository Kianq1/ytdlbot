import os
import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "BOT_TOKEN"

# ذخیره لینک‌ها برای هر کاربر
user_links = {}

async def start(update, context):
    await update.message.reply_text("سلام کیان! لینک یوتیوب رو بفرست تا کیفیت رو انتخاب کنی.")

async def handle_link(update, context):
    url = update.message.text
    user_id = update.message.from_user.id
    user_links[user_id] = url

    await update.message.reply_text("در حال دریافت کیفیت‌ها...")

    # استخراج کیفیت‌ها
    ydl_opts = {"quiet": True}
    formats = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        for f in info["formats"]:
            if f.get("ext") == "mp4" and f.get("height"):
                formats.append((f["format_id"], f"{f['height']}p"))

    # ساخت دکمه‌ها
    buttons = []
    for fmt_id, label in formats:
        buttons.append([InlineKeyboardButton(label, callback_data=f"video_{fmt_id}")])

    # دکمه MP3
    buttons.append([InlineKeyboardButton("فقط صدا (MP3)", callback_data="audio_mp3")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("کیفیت مورد نظر رو انتخاب کن:", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("لینک پیدا نشد. دوباره لینک بفرست.")
        return

    choice = query.data

    if choice.startswith("video_"):
        fmt = choice.split("_")[1]
        await query.edit_message_text(f"در حال دانلود ویدیو با کیفیت {fmt} ...")

        ydl_opts = {
            "format": fmt,
            "outtmpl": "video.mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_video(open("video.mp4", "rb"))
        os.remove("video.mp4")

    elif choice == "audio_mp3":
        await query.edit_message_text("در حال دانلود نسخه MP3 ...")

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.mp3",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_audio(open("audio.mp3", "rb"))
        os.remove("audio.mp3")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    await app.run_polling()

import asyncio
asyncio.run(main())    await app.run_polling()

import asyncio
asyncio.run(main())
