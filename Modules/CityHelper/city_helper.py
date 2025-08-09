from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config
import logging
import requests

class CityHelper:
    """Helper class for city-related operations"""
    
    def __init__(self, temperature: float = 0.7):
        config = Config.from_env()
        self.llm = ChatOpenAI(
            model=config.gpt_model,
            temperature=temperature,
            openai_api_key=config.openai_api_key
        )
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def extract_city_from_message(self, message: str) -> str:
        """Extract city name from user message using LLM"""
        system_prompt = """You are a geography assistant that extracts city names from user messages.
        Analyze the user's message and extract the city name if they are asking about a specific city.
        
        Return only the city name if found, or return "none" if no specific city is mentioned.
        
        Examples:
        - "What time is it in London?" -> "London"
        - "Time in New York" -> "New York"
        - "What's the weather in Katowice?" -> "Katowice"
        - "Sunrise in Tokyo" -> "Tokyo"
        - "What time is it?" -> "none"
        - "Current weather" -> "none"
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]
        
        try:
            response = self.llm.invoke(messages)
            city = response.content.strip()
            return city if city.lower() != "none" else None
        except Exception as e:
            self.logger.error(f"Error extracting city from message '{message}': {str(e)}")
            return None
    
    def normalize_city_name(self, city_name: str) -> str:
        """Normalize city name to its primary form for geocoding"""
        system_prompt = """You are a geography expert. Normalize the given city name to its primary, standard form suitable for geocoding.
        
        Rules:
        - Remove inflected forms (e.g., "Katowicach" -> "Katowice")
        - Keep proper capitalization
        - Preserve Polish characters (ą, ć, ę, ł, ń, ó, ś, ź, ż)
        - Handle multi-word city names properly
        - Return only the city name, nothing else
        
        Examples:
        - "Katowicach" -> "Katowice"
        - "Poznaniu" -> "Poznań"
        - "Ustronie Morskie" -> "Ustronie Morskie"
        - "Warszawie" -> "Warszawa"
        - "London" -> "London"
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=city_name)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            self.logger.error(f"Error normalizing city name '{city_name}': {str(e)}")
            return city_name
    
    def get_coordinates_from_geocoding(self, city_name: str) -> tuple:
        """Get coordinates from OpenWeatherMap geocoding API"""
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": city_name,
            "limit": 1,
            "appid": self.config.open_weather_map_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                return (location['lat'], location['lon'])
            else:
                self.logger.warning(f"No coordinates found for city: {city_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting coordinates for city '{city_name}': {str(e)}")
            return None
