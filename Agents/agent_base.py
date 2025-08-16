from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from Modules.MessageProcessor.message_processor import Message

class AgentBase(ABC):
    """Base interface for all agents in the system"""
    
    def __init__(self, user_id: str, configuration: Dict[str, Any], questionnaire_answers: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.configuration = configuration
        self.questionnaire_answers = questionnaire_answers or {}
    
    @abstractmethod
    def ask(self, message: Message) -> str:
        """Process a user message and return a response"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name"""
        pass
    
    def get_city_info(self, message: str = None) -> tuple:
        """Common method to get city name and coordinates from message or configuration"""
        from Modules.CityHelper import CityHelper
        
        # Initialize city helper if not already done
        if not hasattr(self, 'city_helper'):
            temperature = self.configuration.get('temperature', 0.7)
            self.city_helper = CityHelper(temperature=temperature)
        
        # First, try to extract city from message
        if message:
            city_name = self.city_helper.extract_city_from_message(message)
            if city_name:
                # Normalize city name for geocoding
                normalized_city = self.city_helper.normalize_city_name(city_name)
                coordinates = self.city_helper.get_coordinates_from_geocoding(normalized_city)
                if coordinates:
                    lat, lon = coordinates
                    return (normalized_city, lat, lon)
        
        # If no city in message, get from agent item questionnaire answers
        return self._get_city_from_configuration()
    
    def _get_city_from_configuration(self) -> tuple:
        """Get city coordinates from questionnaire answers"""
        if not hasattr(self, 'questionnaire_answers') or not self.questionnaire_answers:
            raise ValueError("Questionnaire answers not found - city configuration is required")
        
        city_name = self.questionnaire_answers.get('city_name')
        city_lat = self.questionnaire_answers.get('city_lat')
        city_lon = self.questionnaire_answers.get('city_lon')
        
        if city_name and city_lat and city_lon:
            return (city_name, float(city_lat), float(city_lon))
        raise ValueError("City name not found in questionnaire answers")

