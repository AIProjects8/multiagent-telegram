from Agents.agent_base import AgentBase
from langchain_openai import ChatOpenAI
from config import Config
from typing import Any, Callable
from Modules.MessageProcessor.message_processor import Message
from Modules.CityHelper.city_helper import CityHelper

class ConfigurationAgent(AgentBase):
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=0.1,
            max_tokens=500
        )
        self.city_helper = CityHelper()
        self.configuration_steps = {
            'language': self._ask_language,
            'city': self._ask_city
        }
    
    async def ask(self, message: Message, send_message: Callable[[str], Any]) -> str:
        self._save_user_message(message)
        
        if self._is_configuration_complete():
            response = self._("Configuration is already complete. You can now use other agents.")
            self._save_assistant_message(response)
            return self.response(response)
        
        current_step = self._get_current_step()
        
        if current_step == 'language':
            response = self._ask_language(message)
        elif current_step == 'city':
            response = self._ask_city(message)
        else:
            response = self._("Configuration error. Please contact support.")
        
        self._save_assistant_message(response)
        return self.response(response)
    
    def _is_configuration_complete(self) -> bool:
        """Check if user has completed all configuration steps"""
        return self.questionnaire_answers.get('language') and self.questionnaire_answers.get('city')
    
    def _get_current_step(self) -> str:
        """Determine the current configuration step"""
        if not self.questionnaire_answers.get('language'):
            return 'language'
        elif not self.questionnaire_answers.get('city'):
            return 'city'
        return 'complete'
    
    def _ask_language(self, message: Message) -> str:
        """Ask user for their language preference"""
        if self.questionnaire_answers.get('language'):
            return self._("Language is already set. Moving to next step.")
        
        # Check if user provided language in this message
        if message.text and len(message.text.strip()) == 2:
            lang = message.text.strip().lower()
            if lang in ['en', 'pl']:
                self.questionnaire_answers['language'] = lang
                self._save_configuration()
                self.refresh_translator()  # Refresh translator to use new language
                return self._get_city_question()
            else:
                return self._get_language_question(message.ui_language)
        
        return self._get_language_question(message.ui_language)
    
    def _get_language_question(self, ui_language: str) -> str:
        """Get language question in the appropriate UI language"""
        if ui_language == 'pl':
            return """Jaki jest Twój język? Wpisz kod dwuliterowy:
en - English
pl - Polski

Wpisz tylko dwie litery (en lub pl):"""
        else:
            return self._("What is your language? Insert two characters code:\nen - English\npl - Polski\n\nEnter only two characters (en or pl):")
    
    def _ask_city(self, message: Message) -> str:
        """Ask user for their city"""
        if not self.questionnaire_answers.get('language'):
            return self._("Please set language first.")
        
        if self.questionnaire_answers.get('city'):
            return self._("City is already set. Configuration complete.")
        
        # Check if user provided city in this message
        if message.text and len(message.text.strip()) > 0:
            city_name = message.text.strip()
            user_lang = self.questionnaire_answers['language']
            
            # Validate city using geocoding
            try:
                normalized_city = self.city_helper.normalize_city_name(city_name)
                coordinates = self.city_helper.get_coordinates_from_geocoding(normalized_city)
                
                if coordinates:
                    lat, lon = coordinates
                    city_obj = {
                        "name": normalized_city,
                        "lat": lat,
                        "lon": lon
                    }
                    self.questionnaire_answers['city'] = city_obj
                    self._save_configuration()
                    return self._("Configuration completed! You can now use other agents.")
                else:
                    return self._get_city_error_message(user_lang)
            except Exception as e:
                return self._get_city_error_message(user_lang)
        
        return self._get_city_question()
    
    def _get_city_question(self) -> str:
        return self._("What is your city name?")
    
    def _get_city_error_message(self, user_lang: str) -> str:
        """Get city error message in the user's chosen language"""
        if user_lang == 'pl':
            return """Nazwa miasta powinna być w formie podstawowej. Przykłady poprawnych nazw:
- Warszawa (nie Warszawie)
- Katowice (nie Katowicach)
- New York (nie New Yorku)
- London (nie Londynie)
- Paris (nie Paryżu)

Spróbuj ponownie:"""
        else:
            return self._("City name should be in the basic form. Examples of correct names:\n- Warszawa (not Warszawie)\n- Katowice (not Katowicach)\n- New York (not New Yorku)\n- London (not Londynie)\n- Paris (not Paryżu)\n\nPlease try again:")
    
    def _save_configuration(self):
        """Save configuration to database via UserManager"""
        # Use the inherited _user_manager from the base class
        self._user_manager.update_user_configuration(self.user_id, self.questionnaire_answers)
        print(f"Configuration saved for user {self.user_id}")
    
    @property
    def name(self) -> str:
        return "configuration"
