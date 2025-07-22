from sqlalchemy.orm import Session
from .models import User

def create_user(db: Session, telegram_id: int) -> User:
    user = User(telegram_id=telegram_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_telegram_id(db: Session, telegram_id: int) -> User | None:
    return db.query(User).filter(User.telegram_id == telegram_id).first() 