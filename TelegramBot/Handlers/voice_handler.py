from telegram import Update
from telegram.ext import ContextTypes
import os
from config import Config
from TelegramBot.Tools.auth_decorator import restricted
from Modules.SpeechHelper.speech_helper import SpeechHelper
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from SqlDB.user_cache import UserCache
from SqlDB.middleware import update_db_user

@restricted
@update_db_user
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    audio_path = f'./audio/voice_{update.message.voice.file_unique_id}.ogg'
    
    speech_manager = SpeechHelper()
    await speech_manager.download_voice_file(audio_file.file_path, audio_path)
    transcribed_text = await speech_manager.transcribe_voice(audio_path)
    
    # Handle voice processing
    telegram_user_id: int = update.message.from_user.id
    user_id = UserCache().get_user_id(telegram_user_id)
    get_agent_rooter().switch(transcribed_text, user_id)
    
    os.remove(audio_path)
    
    if Config.from_env().voice_response:
        await update.message.reply_text(transcribed_text)
        return
    
    response_audio_path = f'./audio/response_{update.message.message_id}.mp3'
    await speech_manager.text_to_speech("Transcription is working.", response_audio_path)
    
    await update.message.reply_voice(voice=open(response_audio_path, 'rb'))
    os.remove(response_audio_path)