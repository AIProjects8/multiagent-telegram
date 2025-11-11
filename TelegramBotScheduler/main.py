import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from SqlDB.database import init_db
from Modules.Scheduler.scheduler import SchedulerService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting TelegramBotScheduler...")
    
    config = Config.from_env()
    config.validate()
    
    logger.info("Initializing database...")
    init_db()
    
    scheduler_service = SchedulerService(config)
    
    try:
        logger.info("Starting scheduler service...")
        await scheduler_service.start()
        
        logger.info("Scheduler service is running. Press Ctrl+C to stop.")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Error in scheduler service: {e}")
    finally:
        await scheduler_service.stop()
        logger.info("Scheduler service stopped.")

if __name__ == "__main__":
    print("Starting TelegramBotScheduler. Version 0.0.1")
    asyncio.run(main()) 