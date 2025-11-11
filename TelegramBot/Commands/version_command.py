from telegram import Update
from telegram.ext import ContextTypes
from version import VERSION

async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Version: {VERSION}")

