from typing import Dict, Optional
from .models import User

class UserCache:
    _instance = None
    _cache: Dict[int, User] = {}  # telegram_id -> User
    _user_id_cache: Dict[str, int] = {}  # user_id -> telegram_id

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram_id - O(1) access"""
        return self._cache.get(telegram_id)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id (from DB) - O(1) access"""
        telegram_id = self._user_id_cache.get(user_id)
        if telegram_id:
            return self._cache.get(telegram_id)
        return None

    def get_user_id(self, telegram_id: int) -> str:
        """Get user_id (from DB) by telegram_id - O(1) access"""
        user = self.get_user(telegram_id)
        if user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found in cache")
        return str(user.id)

    def get_telegram_id(self, user_id: str) -> Optional[int]:
        """Get telegram_id by user_id (from DB) - O(1) access"""
        return self._user_id_cache.get(user_id)

    def add_user(self, telegram_id: int, user: User) -> None:
        """Add user to both caches - O(1) operation"""
        self._cache[telegram_id] = user
        self._user_id_cache[str(user.id)] = telegram_id

    def has_user(self, telegram_id: int) -> bool:
        """Check if user exists by telegram_id - O(1) access"""
        return telegram_id in self._cache
