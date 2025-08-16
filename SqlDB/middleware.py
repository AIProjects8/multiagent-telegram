from telegram import Update
from telegram.ext import ContextTypes
from .database import Session, engine
from .user_service import get_user_by_telegram_id, create_user
from .user_cache import UserCache
from functools import wraps

def _update_user_in_database(telegram_id: int, chat_id: int, first_name: str, user):
    """Update user in database with new chat_id and/or name"""
    db = Session(engine)
    try:
        db_user = get_user_by_telegram_id(db, telegram_id)
        if db_user:
            if user.chat_id != chat_id:
                db_user.chat_id = chat_id
            if user.name != first_name:
                db_user.name = first_name
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
    finally:
        db.close()
    return None

def _update_cached_user(telegram_id: int, chat_id: int, first_name: str, cached_user):
    """Update cached user and sync with database"""
    user_updated = False
    
    if cached_user.chat_id != chat_id:
        print(f"Chat ID changed for user {telegram_id}: {cached_user.chat_id} -> {chat_id}")
        cached_user.chat_id = chat_id
        user_updated = True
    
    if cached_user.name != first_name:
        print(f"Name changed for user {telegram_id}: {cached_user.name} -> {first_name}")
        cached_user.name = first_name
        user_updated = True
    
    if user_updated:
        updated_user = _update_user_in_database(telegram_id, chat_id, first_name, cached_user)
        if updated_user:
            cache = UserCache()
            cache.add_user(telegram_id, updated_user)
            print(f"Updated user {telegram_id} in database")
    
    return cached_user

def _handle_user_from_database(telegram_id: int, chat_id: int, first_name: str, db: Session, user):
    """Handle user found in database but not in cache"""
    user_updated = False
    
    if user.chat_id != chat_id:
        print(f"Updating chat_id for existing user {telegram_id}: {user.chat_id} -> {chat_id}")
        user.chat_id = chat_id
        user_updated = True
    
    if user.name != first_name:
        print(f"Updating name for existing user {telegram_id}: {user.name} -> {first_name}")
        user.name = first_name
        user_updated = True
    
    if user_updated:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        finally:
            db.close()
    
    return user

def update_db_user(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            print("No effective user found in update")
            return False
            
        telegram_id = update.effective_user.id
        chat_id = update.message.chat.id
        first_name = update.effective_user.first_name
        cache = UserCache()
        
        print(f"Checking user existence for telegram_id: {telegram_id}")
        
        if cache.has_user(telegram_id):
            print(f"User {telegram_id} found in cache")
            cached_user = cache.get_user(telegram_id)
            _update_cached_user(telegram_id, chat_id, first_name, cached_user)
            return await func(update, context, *args, **kwargs)
            
        print(f"User {telegram_id} not in cache, checking database")
        db = Session(engine)
        try:
            user = get_user_by_telegram_id(db, telegram_id)
            if not user:
                print(f"Creating new user for telegram_id: {telegram_id}")
                user = create_user(db, telegram_id, chat_id, first_name)
                user.configuration = None  # New users start with NULL configuration
                db.commit()
                db.refresh(user)
            else:
                print(f"User {telegram_id} found in database")
                user = _handle_user_from_database(telegram_id, chat_id, first_name, db, user)
            
            cache.add_user(telegram_id, user)
            print(f"User {telegram_id} added to cache")
            return await func(update, context, *args, **kwargs)
        finally:
            db.close()
            
    return wrapper 