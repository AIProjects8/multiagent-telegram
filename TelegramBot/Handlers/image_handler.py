from telegram import Update
from telegram.ext import ContextTypes
import os
from TelegramBot.Tools.auth_decorator import restricted
from SqlDB.middleware import update_db_user
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from SqlDB.user_cache import UserCache

@restricted
@update_db_user
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    text = update.message.caption or "Describe what you see on the image."
    file = await context.bot.get_file(photo.file_id)
    
    image_path = f'./images/image_{photo.file_unique_id}.jpg'
    os.makedirs('./images', exist_ok=True)
    await file.download_to_drive(image_path)
    
    # Handle image processing
    telegram_user_id: int = update.message.from_user.id
    user_id = UserCache().get_user_id(telegram_user_id)
    get_agent_rooter().switch(text, user_id)

    await update.message.reply_text("Image processed")
    
    os.remove(image_path)