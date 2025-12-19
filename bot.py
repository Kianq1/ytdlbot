import os
import yt_dlp
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "BOT_TOKEN"

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام کیان! لینک ویدیو یوتیوب رو بفرست تا دانلودش کنم.")

async def download_video(update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("در حال دانلود... لطفاً صبر کن.")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_video(video=open("video.mp4", "rb"))

        os.remove("video.mp4")

    except Exception as e:
        await update.message.reply_text("خطا در دانلود ویدیو. لینک رو چک کن یا VPN رو روشن کن.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    await app.run_polling()

import asyncio
asyncio.run(main())
