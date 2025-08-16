from telegram import Update
from telegram.ext import ContextTypes
from TelegramBot.Tools.auth_decorator import restricted
from SqlDB.middleware import update_db_user
from SqlDB.user_cache import UserCache
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from Modules.MessageProcessor.message_processor import MessageProcessor, Message

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

    # Get user's language from Telegram
    user_language = update.effective_user.language_code or 'en'
    print(f"User language detected: {user_language}")
    
    # Create Message object with text and language
    message_obj = MessageProcessor.create_message(text, user_language)
    
    user_id = UserCache().get_user_id(telegram_user_id)
    switched = get_agent_rooter().switch(message_obj.text, user_id)
    agent = get_agent_rooter().current_agents[user_id]
    if(switched):
        await update.message.reply_text(f"Switched to agent: {agent['name']}")

    if not MessageProcessor.should_process_message(message_obj.text):
        return

    # Get response from agent (translation happens inside the agent)
    response = get_agent_rooter().ask_current_agent(user_id, message_obj)
    await update.message.reply_text(response)