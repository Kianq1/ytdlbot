import yt_dlp
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8580077921:AAEW59TyYEnDQUp5vBdeQyOImyxQkeVgv9U"

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست تا دانلودش کنم.")

async def download(update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("در حال دانلود...")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_video(open("video.mp4", "rb"))

    except Exception as e:
        await update.message.reply_text("خطا در دانلود. لینک یا VPN رو چک کن.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    app.run_polling()

if __name__ == "__main__":
    main()
