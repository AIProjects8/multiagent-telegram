from SqlDB.database import Session, engine
from SqlDB.models import Agent, AgentItem
import os
import json
import gettext
import re
from pathlib import Path
from typing import Optional, Any
from config import Config
from SqlDB.user_cache import UserCache
from .agent_factory import AgentFactory
from Agents.agent_base import AgentBase
from Modules.MessageProcessor.message_processor import Message
from Modules.UserManager.user_manager import UserManager

class AgentRooter:
    _instance = None
    _agents = []
    _agent_map = {}
    _app_keyword = None
    current_agents = {}
    _agent_instances = {}
    _user_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
            cls._instance._load_agents()
        return cls._instance
      
    def _init(self):
        config = Config.from_env()
        self._app_keyword = config.app_keyword.lower()
        self._agents = []
        self._agent_map = {}
        self._default_agent = None
        self._agent_instances = {}
        self._user_manager = UserManager()
        self._translators = {}
        self._user_languages = {}

    def _load_agents(self):
        session = Session(engine)
        try:
            agents = session.query(Agent).all()
            
            for agent in agents:
                keywords = [k.strip().lower() for k in agent.keywords.split(',') if k.strip()]
                agent_configuration = agent.configuration
                if isinstance(agent_configuration, str):
                    agent_configuration = json.loads(agent_configuration)
                agent_obj = {
                    'id': str(agent.id),
                    'name': agent.name,
                    'keywords': keywords,
                    'configuration': agent_configuration,
                    'display_name': agent.display_name
                }
                self._agents.append(agent_obj)
                for kw in keywords:
                    self._agent_map[kw] = agent_obj
                if agent.name == 'default':
                    self._default_agent = agent_obj
        finally:
            session.close()

    def _get_agent_item_questionnaire_data(self, user_id: str, agent_id: str) -> dict:
        session = Session(engine)
        try:
            agent_item = session.query(AgentItem).filter(
                AgentItem.user_id == user_id,
                AgentItem.agent_id == agent_id
            ).first()
            
            if agent_item:
                return agent_item.questionnaire_answers or {}
            return {}
        finally:
            session.close()

    def _get_agent_instance_key(self, user_id: str, agent_name: str) -> str:
        return f"{user_id}_{agent_name}"

    def _get_agent_instance(self, user_id: str, agent_name: str) -> AgentBase:
        instance_key = self._get_agent_instance_key(user_id, agent_name)
        
        if instance_key in self._agent_instances:
            return self._agent_instances[instance_key]
        
        agent_obj = None
        for agent in self._agents:
            if agent['name'] == agent_name:
                agent_obj = agent
                break
        
        if not agent_obj:
            raise ValueError(f"Agent {agent_name} not found")
        
        questionnaire_answers = self._get_agent_item_questionnaire_data(user_id, agent_obj['id'])
        
        agent_instance = AgentFactory.create_agent(
            agent_name=agent_name,
            user_id=user_id,
            agent_id=agent_obj['id'],
            agent_configuration=agent_obj['configuration'],
            questionnaire_answers=questionnaire_answers
        )
        
        self._agent_instances[instance_key] = agent_instance
        return agent_instance

    def find_agent_in_message(self, message: Message):
        msg = message.text.lower()
        for kw, agent in self._agent_map.items():
            search = f"{self._app_keyword} {kw}"
            if search in msg:
                return agent
        return None
    
    def _extract_words(self, text: str) -> list:
        text_lower = text.lower().strip()
        return re.findall(r'\b\w+\b', text_lower)
    
    def _check_invalid_agent_request(self, message: Message) -> Optional[str]:
        msg_lower = message.text.lower().strip()
        app_keyword_pattern = f"{self._app_keyword} "
        
        if app_keyword_pattern not in msg_lower:
            return None
        
        words = self._extract_words(msg_lower)
        if len(words) < 2:
            return None
        
        app_keyword_index = -1
        for i, word in enumerate(words):
            if word == self._app_keyword and i + 1 < len(words):
                app_keyword_index = i
                break
        
        if app_keyword_index == -1:
            return None
        
        requested_keyword = words[app_keyword_index + 1] if app_keyword_index + 1 < len(words) else None
        
        if requested_keyword and requested_keyword not in self._agent_map:
            return requested_keyword
        
        return None
    
    def _get_current_agent(self, user_id: str):
        if user_id not in self.current_agents:
            # Set default agent initially
            self.current_agents[user_id] = self._default_agent
        return self.current_agents[user_id]
    
    def _user_has_configuration(self, user_id: str) -> bool:
        """Check if user has completed configuration using UserManager"""
        return self._user_manager.check_user_configuration(user_id)
    
    def _get_configuration_agent(self):
        """Get the configuration agent object"""
        for agent in self._agents:
            if agent['name'] == 'configuration':
                return agent
        return None
    
    def _get_current_agent_instance(self, user_id: str) -> AgentBase:
        current_agent = self._get_current_agent(user_id)
        if not current_agent:
            return None
            
        return self._get_agent_instance(user_id, current_agent['name'])
    
    def _get_user_language(self, user_id: str) -> str:
        user = self._user_manager.cache.get_user_by_id(user_id)
        if not user or not user.configuration or not user.configuration.get('language'):
            return 'en'
        return user.configuration['language']
    
    def _get_translator(self, user_id: str, language: Optional[str] = None):
        if language is None:
            user_lang = self._get_user_language(user_id)
        else:
            user_lang = language
        
        cache_key = f"{user_id}_{user_lang}" if language else user_id
        
        if language is None:
            if user_id in self._user_languages and self._user_languages[user_id] != user_lang:
                if user_id in self._translators:
                    del self._translators[user_id]
            self._user_languages[user_id] = user_lang
        
        if cache_key in self._translators:
            return self._translators[cache_key]
        
        if user_lang == 'en':
            self._translators[cache_key] = gettext.NullTranslations()
        else:
            try:
                locale_dir = Path(__file__).parent / 'locale'
                mo_file = locale_dir / user_lang / 'LC_MESSAGES' / 'messages.mo'
                
                if mo_file.exists():
                    self._translators[cache_key] = gettext.translation(
                        'messages',
                        localedir=str(locale_dir),
                        languages=[user_lang]
                    )
                else:
                    self._translators[cache_key] = gettext.NullTranslations()
            except Exception as e:
                print(f"Exception creating translator for user {user_id}: {e}")
                self._translators[cache_key] = gettext.NullTranslations()
        return self._translators[cache_key]
    
    def _(self, user_id: str, message: str) -> str:
        translator = self._get_translator(user_id)
        return translator.gettext(message)
    
    def _get_agent_display_name(self, agent: dict, user_language: str) -> str:
        display_name = agent.get('display_name')
        if display_name and isinstance(display_name, dict):
            if user_language in display_name:
                return display_name[user_language]
            if 'en' in display_name:
                return display_name['en']
        return agent['name']
    
    async def ask_current_agent(self, message: Message, send_message: Any, stream_chunk: Any = None) -> str:
        agent_instance = self._get_current_agent_instance(message.user_id)
        if agent_instance:
            return await agent_instance.ask(message, send_message, stream_chunk)
        return "No agent available to respond"

    def check_which_agent_query(self, message: Message) -> Optional[str]:
        user_language = self._get_user_language(message.user_id)
        msg_lower = message.text.lower().strip()
        
        translator = self._get_translator(message.user_id)
        commands_str = translator.gettext("which,what")
        commands = [cmd.strip() for cmd in commands_str.split(',') if cmd.strip()]
        
        if user_language != 'en':
            en_translator = self._get_translator(message.user_id, 'en')
            en_commands_str = en_translator.gettext("which,what")
            en_commands = [cmd.strip() for cmd in en_commands_str.split(',') if cmd.strip()]
            commands.extend(en_commands)
        
        words = self._extract_words(msg_lower)
        
        if len(words) < 2:
            return None
        
        first_word = words[0].strip()
        second_word = words[1].strip() if len(words) > 1 else ""
        
        if first_word in commands and second_word == "agent":
            current_agent = self._get_current_agent(message.user_id)
            if current_agent:
                agent_display_name = self._get_agent_display_name(current_agent, user_language)
                response = self._(message.user_id, "The current agent is: {agent_name}").format(agent_name=agent_display_name)
                return response
        
        return None

    def switch(self, message: Message) -> Optional[str]:
        switched_agent = None
        
        if not self._user_has_configuration(message.user_id):
            configuration_agent = self._get_configuration_agent()
            if configuration_agent and self.current_agents.get(message.user_id) != configuration_agent:
                self.current_agents[message.user_id] = configuration_agent
                switched_agent = configuration_agent
                print(f"User {message.user_id} has no configuration, forced to ConfigurationAgent")
        else:
            agent = self.find_agent_in_message(message)
            temp_current_agent = self._get_current_agent(message.user_id)
            
            if agent and (temp_current_agent is None or agent['id'] != temp_current_agent['id']):
                self.current_agents[message.user_id] = agent
                switched_agent = agent
                print(f"Switched to agent: {agent['id']} for user: {message.user_id}")
            elif agent is None:
                invalid_keyword = self._check_invalid_agent_request(message)
                if invalid_keyword:
                    error_message = self._(message.user_id, "Agent '{agent_name}' does not exist.").format(
                        agent_name=invalid_keyword
                    )
                    return error_message
        
        if switched_agent:
            user_language = self._get_user_language(message.user_id)
            agent_display_name = self._get_agent_display_name(switched_agent, user_language)
            translated_message = self._(message.user_id, "Switched to agent: {agent_name}").format(agent_name=agent_display_name)
            return translated_message
        
        return None

def get_agent_rooter():
    return AgentRooter()
