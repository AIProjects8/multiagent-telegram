from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from Agents.agent_base import AgentBase
from Agents.WeatherAgent.tools import get_weather
from Agents.WeatherAgent.response_formatter import format_weather_response
from config import Config

class WeatherAgent(AgentBase):
    
    def __init__(self, user_id: str, configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, configuration, questionnaire_answers)
        self.config = Config.from_env()
        temperature = self.configuration.get('temperature')
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=temperature
        )
    
    def ask(self, message: str) -> str:
        try:
            city_name, lat, lon = self.get_city_info(message)
            
            if lat is None or lon is None:
                return "Nie mogę podać prognozy pogody bez znajomości nazwy miasta. Proszę podać nazwę miasta lub skonfiguruj domyślne miasto w ustawieniach."
            
            weather_data = get_weather(lat, lon)
            response = format_weather_response(weather_data, lat, lon, city_name)
            return response
            
        except ValueError as e:
            return f"Błąd konfiguracji: {str(e)}"
        except Exception as e:
            return f"Przepraszam, wystąpił błąd podczas pobierania prognozy pogody: {str(e)}"
    
    @property
    def name(self) -> str:
        return "weather" 