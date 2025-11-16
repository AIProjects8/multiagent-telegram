from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import gettext
import logging
from pathlib import Path
from Modules.MessageProcessor.message_processor import Message
from Modules.UserManager.user_manager import UserManager
from Modules.CityHelper import CityHelper
from Modules.ConversationMemory import get_conversation_memory_manager

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    TELEGRAM_MAX_MESSAGE_LENGTH = 4096
 
    def __init__(self, user_id: str, agent_id: str, agent_configuration: Dict[str, Any], questionnaire_answers: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.agent_id = agent_id
        self.agent_configuration = agent_configuration
        self.questionnaire_answers = questionnaire_answers or {}
        self._user_manager = UserManager()
        self._city_helper = None
        self._translator = None
        self._conversation_memory_manager = get_conversation_memory_manager()
        self._chat_history = None
        self._initialize_conversation_memory()
    
    def _initialize_conversation_memory(self):
        self._chat_history = self._conversation_memory_manager.get_chat_history(
            self.user_id, 
            self.agent_id
        )
    
    def _get_user_language(self) -> str:
        user = self._user_manager.cache.get_user_by_id(self.user_id)
        if not user or not user.configuration or not user.configuration.get('language'):
            logger.info(f"User {self.user_id}: No user or language configuration found, returning default language 'en'")
            return 'en'
        user_language = user.configuration['language']
        logger.info(f"User {self.user_id}: Returning user language '{user_language}'")
        return user_language
    
    def _get_translator(self):
        if self._translator is None:
            user_lang = self._get_user_language()
            
            if user_lang == 'en':
                self._translator = gettext.NullTranslations()
            else:
                try:
                    agent_name = self.name.capitalize() + "Agent"
                    agent_dir = Path(__file__).parent / agent_name
                    locale_dir = agent_dir / 'locale'
                    mo_file = locale_dir / user_lang / 'LC_MESSAGES' / 'messages.mo'
                    
                    if mo_file.exists():
                        self._translator = gettext.translation(
                            'messages',
                            localedir=str(locale_dir),
                            languages=[user_lang]
                        )
                    else:
                        self._translator = gettext.NullTranslations()
                except Exception as e:
                    print(f"Exception creating translator: {e}")
                    self._translator = gettext.NullTranslations()
        return self._translator
    
    def refresh_translator(self):
        self._translator = None
    
    def _(self, message: str) -> str:
        translator = self._get_translator()
        return translator.gettext(message)
    
    def _save_user_message(self, message: Message):
        if self._chat_history and message:
            self._chat_history.add_user_message(message.text)
    
    def _save_assistant_message(self, message: str):
        if self._chat_history and message:
            self._chat_history.add_ai_message(message)
    
    def _save_tool_call(self, message: str):
        if self._chat_history and message:
            self._chat_history.add_tool_call(message)
    
    def _get_chat_history(self):
        if self._chat_history:
            return self._chat_history.messages
        return []
    
    def _truncate_message(self, message: str) -> str:
        if len(message) > self.TELEGRAM_MAX_MESSAGE_LENGTH:
            return message[:self.TELEGRAM_MAX_MESSAGE_LENGTH - 3] + "..."
        return message
    
    def response(self, content: str) -> str:
        return self._truncate_message(content)
    
    def clear_conversation_history(self):
        if self._chat_history:
            self._chat_history.clear()
    
    @abstractmethod
    async def ask(self, message: Message, bot: Optional[Any] = None, chat_id: Optional[int] = None) -> str:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    def get_city_info(self, message: Message = None) -> tuple:

        if self._city_helper is None:
            temperature = self.agent_configuration.get('temperature', 0.7)
            self._city_helper = CityHelper(temperature=temperature)
        
        if message:
            city_name = self._city_helper.extract_city_from_message(message.text)
            if city_name:
                normalized_city = self._city_helper.normalize_city_name(city_name)
                coordinates = self._city_helper.get_coordinates_from_geocoding(normalized_city)
                if coordinates:
                    lat, lon = coordinates
                    return (normalized_city, lat, lon)
        
        return self._get_city_from_user_configuration()
    
    def _get_city_from_user_configuration(self) -> tuple:
        return self._user_manager.get_user_city_info(self.user_id)

