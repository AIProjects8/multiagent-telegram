from telegram import Update
from telegram.ext import ContextTypes
import os
from config import Config
from TelegramBot.Tools.auth_decorator import restricted
from Modules.SpeechHelper.speech_helper import SpeechHelper
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from SqlDB.user_cache import UserCache
from SqlDB.middleware import update_db_user
from Modules.MessageProcessor.message_processor import MessageProcessor, Message
from Modules.UserManager.user_manager import UserManager

@restricted
@update_db_user
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    audio_path = f'./audio/voice_{update.message.voice.file_unique_id}.ogg'
    
    speech_manager = SpeechHelper()
    await speech_manager.download_voice_file(audio_file.file_path, audio_path)
    transcribed_text = await speech_manager.transcribe_voice(audio_path)
    
    ui_language = update.effective_user.language_code or 'en'
    
    telegram_user_id: int = update.message.from_user.id
    user_cache = UserCache()
    user_id = user_cache.get_user_id(telegram_user_id)
    
    user_manager = UserManager()
    try:
        user_language = user_manager.get_user_language(user_id)
        print(f"Voice message user configured language: {user_language}")
    except ValueError:
        user_language = 'en'
    
    message_obj = MessageProcessor.create_message(transcribed_text, user_language, ui_language, user_id)
    
    switched = get_agent_rooter().switch(message_obj)
    
    if switched:
        await update.message.reply_text(f"Switched to agent: {get_agent_rooter().current_agents[user_id]['name']}")
    
    if not MessageProcessor.should_process_message(message_obj.text):
        return
    
    os.remove(audio_path)
    
    if Config.from_env().voice_response:
        await update.message.reply_text(transcribed_text)
        return
    
    chat_id = update.effective_chat.id
    bot = context.bot
    
    response = await get_agent_rooter().ask_current_agent(message_obj, bot, chat_id)
    
    response_audio_path = f'./audio/response_{update.message.message_id}.mp3'
    await speech_manager.text_to_speech(response, response_audio_path)
    
    await update.message.reply_voice(voice=open(response_audio_path, 'rb'))
    os.remove(response_audio_path)