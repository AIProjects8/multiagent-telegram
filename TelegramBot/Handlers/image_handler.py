from telegram import Update
from telegram.ext import ContextTypes
import os
from TelegramBot.Tools.auth_decorator import restricted
from SqlDB.middleware import update_db_user
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from SqlDB.user_cache import UserCache
from Modules.MessageProcessor.message_processor import MessageProcessor, Message
from Modules.UserManager.user_manager import UserManager

@restricted
@update_db_user
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    text = update.message.caption or "Describe what you see on the image."
    file = await context.bot.get_file(photo.file_id)
    
    image_path = f'./images/image_{photo.file_unique_id}.jpg'
    os.makedirs('./images', exist_ok=True)
    await file.download_to_drive(image_path)
    
    ui_language = update.effective_user.language_code or 'en'
    
    telegram_user_id: int = update.message.from_user.id
    user_cache = UserCache()
    user_id = user_cache.get_user_id(telegram_user_id)
    
    user_manager = UserManager()
    try:
        user_language = user_manager.get_user_language(user_id)
    except ValueError:
        user_language = 'en'
    
    message_obj = MessageProcessor.create_message(text, user_language, ui_language, user_id)
    
    get_agent_rooter().switch(message_obj)

    await update.message.reply_text("Image processed")
    
    os.remove(image_path)