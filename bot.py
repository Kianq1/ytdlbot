from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = "BOT_TOKEN"

async def start(update, context):
    await update.message.reply_text("بات روشنه!")

async def echo(update, context):
    await update.message.reply_text("پیامت رسید.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
