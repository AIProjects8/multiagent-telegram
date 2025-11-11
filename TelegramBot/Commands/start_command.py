from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from version import VERSION

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id: int = update.effective_user.id
    await update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm {Config.from_env().bot_username} ({VERSION})")
    await update.message.reply_text(f"Your user ID is: {user_id}. Use it for setting up allowed users in server configuration.")
    