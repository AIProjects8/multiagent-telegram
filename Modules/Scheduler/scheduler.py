import logging
import tempfile
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from SqlDB.database import get_db
from SqlDB.models import Scheduler, User
from uuid import UUID
from AgentsCore.Rooter.agent_rooter import get_agent_rooter
from Modules.MessageProcessor.message_processor import MessageProcessor
from Modules.SpeechHelper.speech_helper import SpeechHelper
from config import Config

class SchedulerService:
    def __init__(self, config: Config):
        self.config = config
        self.bot = Bot(token=config.telegram_bot_token)
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    async def start(self):
        self.logger.info("Starting Scheduler Service")
        try:
            self.scheduler.start()
            await self._load_scheduler_configuration()
            self.running = True
            self.logger.info("Scheduler Service started successfully")
        except Exception as e:
            self.logger.error(f"Error starting scheduler service: {e}")
            raise e
    
    async def stop(self):
        if self.running:
            self.logger.info("Stopping Scheduler Service")
            self.scheduler.shutdown()
            self.running = False
            self.logger.info("Scheduler Service stopped")
    
    async def _load_scheduler_configuration(self):
        self.logger.info("Loading scheduler configuration from database")
        db = next(get_db())
        try:
            scheduler_configs = db.query(Scheduler).all()
            
            for config in scheduler_configs:
                await self._schedule_message(config)
                
            self.logger.info(f"Loaded {len(scheduler_configs)} scheduler configurations")
        except Exception as e:
            self.logger.error(f"Error loading scheduler configuration: {e}")
            raise e
        finally:
            db.close()
    
    async def _schedule_message(self, scheduler_config: Scheduler):
        try:
            user_id_str = str(scheduler_config.user_id)
            agent_id_str = str(scheduler_config.agent_id)
            job_id = str(scheduler_config.id)
            
            self.logger.info(f"Scheduling message for user {user_id_str} and agent {agent_id_str} at {scheduler_config.time}")
            
            self.scheduler.add_job(
                func=self._send_scheduled_message,
                trigger=CronTrigger(hour=scheduler_config.time.hour, minute=scheduler_config.time.minute),
                id=job_id,
                name=f'Scheduled message for user {user_id_str} and agent {agent_id_str} at {scheduler_config.time}',
                replace_existing=True,
                args=[user_id_str, scheduler_config.prompt, scheduler_config.message_type]
            )
            
            self.logger.info(f"Successfully scheduled message for user {user_id_str} and agent {agent_id_str} at {scheduler_config.time}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling message for user {scheduler_config.user_id} and agent {scheduler_config.agent_id}: {e}")
    
    async def _send_scheduled_message(self, user_id: str, prompt: str, message_type: str = 'text'):
        try:
            db = next(get_db())
            try:
                user_uuid = UUID(user_id)
                user = db.query(User).filter(User.id == user_uuid).first()
                
                if not user:
                    self.logger.warning(f"User with id {user_id} not found")
                    return
                
                text = MessageProcessor.clean_message(prompt)
                agent_rooter = get_agent_rooter()
                agent_rooter.switch(text, user_id)
                response = agent_rooter.ask_current_agent(user_id, text)
                
                if message_type == 'voice':
                    await self._send_voice_message(user.chat_id, response, user.telegram_id)
                else:
                    await self.bot.send_message(
                        chat_id=user.chat_id,
                        text=response
                    )
                    self.logger.info(f"Sent scheduled text message to user {user.telegram_id}")
                    
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"Error sending scheduled message to user {user_id}: {e}")
    
    async def _send_voice_message(self, chat_id: int, text: str, user_telegram_id: int):
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            speech_helper = SpeechHelper()
            await speech_helper.text_to_speech(text, temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await self.bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_file
                )
            self.logger.info(f"Sent scheduled voice message to user {user_telegram_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending voice message to user {user_telegram_id}: {e}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path) 