from telegram import Update
from telegram.ext import ContextTypes
from TelegramBot.Tools.auth_decorator import restricted
from SqlDB.middleware import update_db_user
from SqlDB.user_cache import UserCache
from AgentsCore.Rooter.agent_rooter import get_agent_rooter

@restricted
@update_db_user
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if(not update.message):
        print("No message")
        return
    
    message_type: str = update.message.chat.type
    text: str = update.message.text
    telegram_user_id: int = update.message.from_user.id
    
    print(f"User ({telegram_user_id}) in {message_type}: {text}")
    
    if message_type == "group":
        await update.message.reply_text("Group chats are not supported yet.")
        return

    # Handle text processing

    user_id = UserCache().get_user_id(telegram_user_id)
    switched = get_agent_rooter().switch(text, user_id)
    agent = get_agent_rooter().current_agent
    if(switched):
        await update.message.reply_text(f"Switched to agent: {agent['name']}")
    else:
        await update.message.reply_text(f"Agent already set: {agent['name']}")

    # await update.message.reply_text("Text processed")