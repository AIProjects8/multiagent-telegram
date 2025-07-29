from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from sqlalchemy.orm import Session
from SqlDB.database import get_db
from SqlDB.models import Scheduler, User
from datetime import time
import logging
from uuid import UUID

class SchedulerService:
    def __init__(self, app: Application):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        self.scheduler.start()
        self._load_scheduler_configuration()
        self.logger.info("Scheduler started")
    
    def stop(self):
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")
    
    def _load_scheduler_configuration(self):
        try:
            db = next(get_db())
            try:
                scheduler_configs = db.query(Scheduler).all()
                
                for config in scheduler_configs:
                    self._schedule_message(config)
                    
                self.logger.info(f"Loaded {len(scheduler_configs)} scheduler configurations")
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Error loading scheduler configuration: {e}")
    
    def _schedule_message(self, scheduler_config: Scheduler):
        try:
            user_id_str = str(scheduler_config.user_id)
            agent_id_str = str(scheduler_config.agent_id)
            job_id = f"scheduler_{user_id_str}_{agent_id_str}"
            
            self.scheduler.add_job(
                func=self._send_scheduled_message,
                trigger=CronTrigger(hour=scheduler_config.time.hour, minute=scheduler_config.time.minute),
                id=job_id,
                name=f'Scheduled message for user {user_id_str} and agent {agent_id_str}',
                replace_existing=True,
                args=[user_id_str, scheduler_config.prompt]
            )
            
            self.logger.info(f"Scheduled message for user {user_id_str} and agent {agent_id_str} at {scheduler_config.time}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling message for user {scheduler_config.user_id} and agent {scheduler_config.agent_id}: {e}")
    
    async def _send_scheduled_message(self, user_id: str, prompt: str):
        try:
            db = next(get_db())
            try:
                user_uuid = UUID(user_id)
                user = db.query(User).filter(User.id == user_uuid).first()
                if user:
                    await self.app.bot.send_message(
                        chat_id=user.chat_id,
                        text=prompt
                    )
                    self.logger.info(f"Sent scheduled message to user {user.telegram_id}")
                else:
                    self.logger.warning(f"User with id {user_id} not found")
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Error sending scheduled message to user {user_id}: {e}")