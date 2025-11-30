from telegram import Update
from telegram.ext import ContextTypes
from TelegramBot.Tools.auth_decorator import restricted
from TelegramBot.Tools.streaming_handler import TelegramStreamingHandler
from SqlDB.middleware import update_db_user
from SqlDB.user_cache import UserCache
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from Modules.MessageProcessor.message_processor import MessageProcessor, Message
from Modules.UserManager.user_manager import UserManager

@restricted
@update_db_user
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    telegram_user_id: int = update.message.from_user.id
    
    print(f"User ({telegram_user_id}) in {message_type}: {text}")
    
    if message_type == "group":
        await update.message.reply_text("Group chats are not supported yet.")
        return

    ui_language = update.effective_user.language_code or 'en'
    
    user_cache = UserCache()
    user_id = user_cache.get_user_id(telegram_user_id)
    
    user_manager = UserManager()
    try:
        user_language = user_manager.get_user_language(user_id)
    except ValueError:
        user_language = 'en'

    message_obj = MessageProcessor.create_message(text, user_language, ui_language, user_id)
    
    switched = get_agent_rooter().switch(message_obj)
    agent = get_agent_rooter().current_agents[user_id]
    if switched:
        await update.message.reply_text(f"Switched to agent: {agent['name']}")

    if not MessageProcessor.should_process_message(message_obj.text):
        return

    async def send_message(text: str):
        await update.message.reply_text(text)
    
    streaming_handler = TelegramStreamingHandler(update)
    response = await get_agent_rooter().ask_current_agent(message_obj, send_message, streaming_handler.stream_chunk)
    
    await streaming_handler.finalize(response)