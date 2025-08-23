from datetime import datetime, UTC
from .tools import get_sunrise, get_sunset
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config
from Agents.agent_base import AgentBase
from Modules.MessageProcessor.message_processor import Message

from timezonefinder import TimezoneFinder
import pytz

class TimeAgent(AgentBase):
    def __init__(self, user_id: str, configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, configuration, questionnaire_answers)
        self.description = "Agent responsible for time information, sunrise and sunset times"
        config = Config.from_env()
        
        # Validate temperature configuration
        if 'temperature' not in configuration:
            raise ValueError("Temperature configuration not found for time agent")
        temperature = configuration['temperature']
        
        # Initialize LLM for query classification
        self.llm = ChatOpenAI(
            model=config.gpt_model,
            temperature=temperature,
            openai_api_key=config.openai_api_key
        )
        
    
    @property
    def name(self) -> str:
        return "time"
        
    def ask(self, message: Message) -> str:
        try:
            city_info = self.get_city_info(message)
            self.current_city_name, self.current_city_lat, self.current_city_lon = city_info
        except ValueError as e:
            return self._("Configuration error: {error}").format(error=str(e))
        except Exception as e:
            return self._("Error getting city information: {error}").format(error=str(e))
        
        # Use LangChain to determine what the user is asking for
        query_type = self._determine_query_type(message.text)
        
        if query_type == "sunrise":
            return self._handle_sunrise_query()
        elif query_type == "sunset":
            return self._handle_sunset_query()
        elif query_type == "time":
            return self._get_current_time()
        else:
            return self._("I'm sorry, I don't understand your request. Please try again.")
    
    def _determine_query_type(self, message: str) -> str:
        system_prompt = f"""You are a time agent that helps users get information about time including:
        - current time
        - time in a specific city
        - time in a specific country
        - sunrise time 
        - sunset time
        - sunrise time in a specific city
        - sunset time in a specific city
        - sunrise time in a specific country
        - sunset time in a specific country
        
        Analyze the user's message and determine what they are asking for.
        
        Return one of the following:
        - "sunrise" if the user is asking about sunrise, dawn, morning sun, etc.
        - "sunset" if the user is asking about sunset, dusk, evening sun, etc.
        - "time" if the user is asking about current time or general time information
        
        Examples:
        - "When does the sun rise?" -> sunrise
        - "What time is sunset?" -> sunset
        - "What time is it?" -> time
        
        Remember to return word without quotes.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip().lower()
        except Exception as e:
            print("Error determining query type: ", e)
            return self._("An error occurred while determining the query type.")
    
    def _handle_sunrise_query(self) -> str:
        try:
            result = get_sunrise(self.current_city_lat, self.current_city_lon, self.current_city_name)
            
            if result.get("success"):
                today_time = result["today_time"]
                tomorrow_time = result["tomorrow_time"]
                today_passed = result["today_passed"]
                
                if today_passed:
                    return self._("The sunrise in {city} will be tomorrow at {time}.").format(city=self.current_city_name, time=tomorrow_time)
                else:
                    return self._("The sunrise in {city} will be at {time}.").format(city=self.current_city_name, time=today_time)
            else:
                return self._("Error: {error}").format(error=result.get('error', 'Failed to get sunrise information'))
                
        except Exception as e:
            return self._("Error getting sunrise information: {error}").format(error=str(e))
    
    def _handle_sunset_query(self) -> str:
        try:
            result = get_sunset(self.current_city_lat, self.current_city_lon, self.current_city_name)
            
            if result.get("success"):
                today_time = result["today_time"]
                tomorrow_time = result["tomorrow_time"]
                today_passed = result["today_passed"]
                
                if today_passed:
                    return self._("The sunset in {city} will be tomorrow at {time}.").format(city=self.current_city_name, time=tomorrow_time)
                else:
                    return self._("The sunset in {city} will be at {time}.").format(city=self.current_city_name, time=today_time)
            else:
                return self._("Error: {error}").format(error=result.get('error', 'Failed to get sunset information'))
                
        except Exception as e:
            return self._("Error getting sunset information: {error}").format(error=str(e))
    
    def _get_current_time(self) -> str:
        # Get the actual time for the city based on its coordinates
        city_time = self._get_time_for_location(self.current_city_lat, self.current_city_lon)
        formatted_time = city_time.strftime("%H:%M")
        
        # Check if the city in the message matches the user's configured city
        try:
            user = self._user_manager.cache.get_user_by_id(self.user_id)
            if user and user.configuration and user.configuration.get('city'):
                user_city_name = user.configuration['city'].get('name', '').lower()
                message_city_name = self.current_city_name.lower()
                
                if user_city_name == message_city_name:
                    # Same city as user's configuration - return just time
                    return formatted_time
                else:
                    # Different city - return time with city name
                    return self._("The time in {city} is {time}").format(city=self.current_city_name, time=formatted_time)
            else:
                # No user configuration - return just time
                return formatted_time
        except Exception:
            # Fallback - return just time
            return formatted_time
    
    def _get_time_for_location(self, lat: float, lon: float) -> datetime:
        """Get the current time for a specific city based on its coordinates"""
        try:
            # Find the timezone for the given coordinates
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=lat, lng=lon)
            
            if timezone_str:
                # Get the timezone object
                city_timezone = pytz.timezone(timezone_str)
                
                # Get current UTC time and convert to city timezone
                utc_now = datetime.now(UTC)
                city_time = utc_now.astimezone(city_timezone)
                
                return city_time
            else:
                # Fallback to UTC if timezone cannot be determined
                return datetime.now(UTC)
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting time for coordinates ({lat}, {lon}): {str(e)}")
            # Fallback to UTC
            return datetime.now(UTC)
    

