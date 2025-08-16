from typing import Optional, Tuple
from SqlDB.user_cache import UserCache
from SqlDB.database import Session, engine
from SqlDB.models import User

class UserManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.cache = UserCache()
            self._initialized = True
    
    def get_user_language(self, user_id: str) -> str:
        user = self.cache.get_user_by_id(user_id)
        if not user or not user.configuration or not user.configuration.get('language'):
            raise ValueError("User language not configured")
        return user.configuration['language']
    
    def get_user_configuration(self, user_id: str) -> Optional[dict]:
        user = self.cache.get_user_by_id(user_id)
        return user.configuration if user else None
    
    def check_user_configuration(self, user_id: str) -> bool:
        user = self.cache.get_user_by_id(user_id)
        if not user or not user.configuration:
            return False
        
        config = user.configuration
        language_ok = config.get('language') in ['en', 'pl']
        city_ok = config.get('city') and isinstance(config['city'], dict)
        
        if city_ok:
            city_config = config['city']
            city_ok = (
                city_config.get('name') and 
                city_config.get('lat') is not None and 
                city_config.get('lon') is not None
            )
        
        return language_ok and city_ok
    
    def update_user_configuration(self, user_id: str, configuration: dict) -> None:
        user = self.cache.get_user_by_id(user_id)
        if user:
            user.configuration = configuration
            # Update in database
            db = Session(engine)
            try:
                db_user = db.query(User).filter(User.id == user.id).first()
                if db_user:
                    db_user.configuration = configuration
                    db.commit()
                    print(f"Updated configuration for user {user_id}")
            finally:
                db.close()
    
    def get_user_city_info(self, user_id: str) -> Tuple[str, float, float]:
        user = self.cache.get_user_by_id(user_id)
        if not user or not user.configuration or not user.configuration.get('city'):
            raise ValueError("User city not configured")
        
        city_config = user.configuration['city']
        if not all(key in city_config for key in ['name', 'lat', 'lon']):
            raise ValueError("User city configuration incomplete")
        
        return city_config['name'], city_config['lat'], city_config['lon']

