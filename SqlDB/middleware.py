from telegram import Update
from telegram.ext import ContextTypes
from .database import get_db
from .user_service import get_user_by_telegram_id, create_user
from .user_cache import UserCache
from functools import wraps

def update_db_user(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return False
            
        telegram_id = update.effective_user.id
        cache = UserCache()
        
        if cache.has_user(telegram_id):
            return await func(update, context, *args, **kwargs)
            
        db = next(get_db())
        try:
            user = get_user_by_telegram_id(db, telegram_id)
            if not user:
                user = create_user(db, telegram_id)
            cache.add_user(telegram_id, user)
            return await func(update, context, *args, **kwargs)
        finally:
            db.close()
            
    return wrapper 