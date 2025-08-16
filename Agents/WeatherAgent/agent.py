from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from Agents.agent_base import AgentBase
from Agents.WeatherAgent.tools import get_weather
from Agents.WeatherAgent.response_formatter import format_weather_response
from config import Config
from Modules.MessageProcessor.message_processor import Message
from Modules.TranslationTools.translator import Translator

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
        self.translator = Translator()
    
    def ask(self, message: Message) -> str:
            if message.language == 'pl':
                return self.translator.translate_to_polish(self._get_response(message))
            else:
                return self._get_response(message)

    def _get_response(self, message: Message) -> str:
        try:
            city_name, lat, lon = self.get_city_info(message.text)
            
            if lat is None or lon is None:
                return "I can't provide a weather forecast without knowing the city name. Please provide the city name or configure the default city in the settings."
            
            weather_data = get_weather(lat, lon)
            response = format_weather_response(weather_data, lat, lon, city_name)
            
            return response
            
        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Sorry, an error occurred while fetching the weather forecast: {str(e)}"
    
    @property
    def name(self) -> str:
        return "weather" 