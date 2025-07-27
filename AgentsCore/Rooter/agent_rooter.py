from SqlDB.database import Session, engine
from SqlDB.models import Agent, AgentItem
import os
import json
from config import Config
from SqlDB.user_cache import UserCache
from .agent_factory import AgentFactory
from Agents.agent_base import AgentBase

class AgentRooter:
    _instance = None
    _agents = []
    _agent_map = {}
    _app_keyword = None
    current_agents = {}
    _agent_instances = {}

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

    def _load_agents(self):
        session = Session(engine)
        try:
            agents = session.query(Agent).all()
            
            for agent in agents:
                keywords = [k.strip().lower() for k in agent.keywords.split(',') if k.strip()]
                configuration = agent.configuration
                if isinstance(configuration, str):
                    configuration = json.loads(configuration)
                agent_obj = {
                    'id': str(agent.id),
                    'name': agent.name,
                    'keywords': keywords,
                    'configuration': configuration
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
            configuration=agent_obj['configuration'],
            questionnaire_answers=questionnaire_answers
        )
        
        self._agent_instances[instance_key] = agent_instance
        return agent_instance

    def find_agent_in_message(self, message: str):
        msg = message.lower()
        for kw, agent in self._agent_map.items():
            search = f"{self._app_keyword} {kw}"
            if search in msg:
                return agent
        return None

    def get_current_agent(self, user_id: str):
        if user_id not in self.current_agents:
            self.current_agents[user_id] = self._default_agent
        return self.current_agents[user_id]
    
    def get_current_agent_instance(self, user_id: str) -> AgentBase:
        current_agent = self.get_current_agent(user_id)
        if not current_agent:
            return None
            
        return self._get_agent_instance(user_id, current_agent['name'])
    
    def ask_current_agent(self, user_id: str, message: str) -> str:
        agent_instance = self.get_current_agent_instance(user_id)
        if agent_instance:
            return agent_instance.ask(message)
        return "No agent available to respond"

    def switch(self, message: str, user_id: str) -> bool:
        agent = self.find_agent_in_message(message)
        temp_current_agent = self.get_current_agent(user_id)
        if agent and (temp_current_agent is None or agent['id'] != temp_current_agent['id']):
            self.current_agents[user_id] = agent
            print(f"Switched to agent: {agent['id']} for user: {user_id}")
            return True
        return False

def get_agent_rooter():
    return AgentRooter()
