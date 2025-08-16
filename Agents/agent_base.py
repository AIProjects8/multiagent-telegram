from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from Modules.MessageProcessor.message_processor import Message
from Modules.UserManager.user_manager import UserManager
from Modules.CityHelper import CityHelper

class AgentBase(ABC):
    """Base interface for all agents in the system"""
    
    def __init__(self, user_id: str, configuration: Dict[str, Any], questionnaire_answers: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.configuration = configuration
        self.questionnaire_answers = questionnaire_answers or {}
        self._user_manager = UserManager()
        self._city_helper = None
    
    @abstractmethod
    def ask(self, message: Message) -> str:
        """Process a user message and return a response"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name"""
        pass
    
    def get_city_info(self, message: Message = None) -> tuple:
        """Common method to get city name and coordinates from message or configuration"""

        if self._city_helper is None:
            temperature = self.configuration.get('temperature', 0.7)
            self._city_helper = CityHelper(temperature=temperature)
        
        # First, try to extract city from message
        if message:
            city_name = self._city_helper.extract_city_from_message(message.text)
            if city_name:
                # Normalize city name for geocoding
                normalized_city = self._city_helper.normalize_city_name(city_name)
                coordinates = self._city_helper.get_coordinates_from_geocoding(normalized_city)
                if coordinates:
                    lat, lon = coordinates
                    return (normalized_city, lat, lon)
        
        # If no city in message, get from user configuration
        return self._get_city_from_user_configuration()
    
    def _get_city_from_user_configuration(self) -> tuple:
        """Get city coordinates from user configuration via UserManager"""
        return self._user_manager.get_user_city_info(self.user_id)

