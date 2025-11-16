from langchain_openai import ChatOpenAI
from Agents.agent_base import AgentBase
from Agents.WeatherAgent.tools import get_weather
from Agents.WeatherAgent.response_formatter import format_weather_response
from config import Config
from typing import Optional, Any
from Modules.MessageProcessor.message_processor import Message

class WeatherAgent(AgentBase):
    
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.config = Config.from_env()
        temperature = self.agent_configuration.get('temperature')
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=temperature
        )
    
    async def ask(self, message: Message, bot: Optional[Any] = None, chat_id: Optional[int] = None) -> str:
        self._save_user_message(message)
        response = self._get_response(message)
        self._save_assistant_message(response)
        return self.response(response)

    def _get_response(self, message: Message) -> str:
        try:
            city_name, lat, lon = self.get_city_info(message)
            
            if lat is None or lon is None:
                return self._("I can't provide a weather forecast without knowing the city name. Please provide the city name or configure the default city in the settings.")
            
            weather_data = get_weather(lat, lon)
            response = format_weather_response(weather_data, city_name, self._)
            
            return response
            
        except ValueError as e:
            return self._("Configuration error: {error}").format(error=str(e))
        except Exception as e:
            return self._("Sorry, an error occurred while fetching the weather forecast: {error}").format(error=str(e))
    
    @property
    def name(self) -> str:
        return "weather" 