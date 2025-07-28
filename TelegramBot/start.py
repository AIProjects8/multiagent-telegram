from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from TelegramBot.Handlers.image_handler import handle_image
from TelegramBot.Handlers.voice_handler import handle_voice
from TelegramBot.Handlers.text_handler import handle_text
from TelegramBot.Commands.start_command import start_command
from TelegramBot.Commands.help_command import help_command
from TelegramBot.Handlers.errors_handler import error
from SqlDB.database import init_db
from Modules.Scheduler.scheduler import SchedulerService

config = Config.from_env()
config.validate()

def start():
    print("Starting bot...")
    
    print("Initializing database...")
    init_db()
    
    app = Application.builder().token(config.telegram_bot_token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    app.add_error_handler(error)
    
    scheduler = SchedulerService(app)
    scheduler.start()
    
    print("Bot is running...")
    app.run_polling(poll_interval=3)