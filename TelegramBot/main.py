import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from version import VERSION
from TelegramBot.Handlers.image_handler import handle_image
from TelegramBot.Handlers.voice_handler import handle_voice
from TelegramBot.Handlers.text_handler import handle_text
from TelegramBot.Commands.start_command import start_command
from TelegramBot.Commands.help_command import help_command
from TelegramBot.Commands.version_command import version_command
from TelegramBot.Handlers.errors_handler import error
import logging

config = Config.from_env()
config.validate()

def start():
    print("Starting bot...")
    
    app = Application.builder().token(config.telegram_bot_token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("version", version_command))
    
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    app.add_error_handler(error)
    
    print("Bot is running...")
    app.run_polling(poll_interval=3)
    
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    print(f"Starting telegram bot. Version {VERSION}")
    
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('telegram.ext').setLevel(logging.WARNING)
    logging.getLogger('telegram.request').setLevel(logging.WARNING)
    logging.getLogger('telegram.ext._application').setLevel(logging.WARNING)
    
    start()