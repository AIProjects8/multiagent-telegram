from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from sqlalchemy.orm import Session
from SqlDB.database import get_db
from SqlDB.models import Scheduler, User
from datetime import time
import logging

class SchedulerService:
    def __init__(self, app: Application):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        self.scheduler.start()
        self._schedule_daily_messages()
        self.logger.info("Scheduler started")
    
    def stop(self):
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")
    
    def _schedule_daily_messages(self):
        self.scheduler.add_job(
            func=self._send_daily_messages,
            trigger=CronTrigger(hour=00, minute=19),
            id='daily_messages',
            name='Send daily messages at 7 AM',
            replace_existing=True
        )
        self.logger.info("Scheduled daily messages at 7:00 AM")
    
    async def _send_daily_messages(self):
        try:
            db = next(get_db())
            try:
                scheduled_messages = db.query(Scheduler).all()
                
                for scheduled_msg in scheduled_messages:
                    user = db.query(User).filter(User.id == scheduled_msg.user_id).first()
                    if user:
                        try:
                            await self.app.bot.send_message(
                                chat_id=user.chat_id,
                                text=scheduled_msg.prompt
                            )
                            self.logger.info(f"Sent scheduled message to user {user.telegram_id}")
                        except Exception as e:
                            self.logger.error(f"Failed to send scheduled message to user {user.telegram_id}: {e}")
            finally:
                db.close()
                            
        except Exception as e:
            self.logger.error(f"Error in daily message scheduler: {e}")
    
    # def add_scheduled_message(self, user_id: str, agent_id: str, prompt: str, schedule_time: time = time(7, 0)):
    #     try:
    #         db = next(get_db())
    #         try:
    #             scheduled_msg = Scheduler(
    #                 user_id=user_id,
    #                 agent_id=agent_id,
    #                 time=schedule_time,
    #                 prompt=prompt
    #             )
    #             db.add(scheduled_msg)
    #             db.commit()
    #             self.logger.info(f"Added scheduled message for user {user_id}")
    #             return scheduled_msg.id
    #         finally:
    #             db.close()
    #     except Exception as e:
    #         self.logger.error(f"Failed to add scheduled message: {e}")
    #         return None
    
    # def remove_scheduled_message(self, user_id: str, agent_id: str):
    #     try:
    #         db = next(get_db())
    #         try:
    #             scheduled_msg = db.query(Scheduler).filter(
    #                 Scheduler.user_id == user_id,
    #                 Scheduler.agent_id == agent_id
    #             ).first()
                
    #             if scheduled_msg:
    #                 db.delete(scheduled_msg)
    #                 db.commit()
    #                 self.logger.info(f"Removed scheduled message for user {user_id}")
    #                 return True
    #             return False
    #         finally:
    #             db.close()
    #     except Exception as e:
    #         self.logger.error(f"Failed to remove scheduled message: {e}")
    #         return False 