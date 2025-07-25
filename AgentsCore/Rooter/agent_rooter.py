from SqlDB.database import Session, engine
from SqlDB.models import Agent
import os
import json
from config import Config
from SqlDB.user_cache import UserCache

class AgentRooter:
    _instance = None
    _agents = []
    _agent_map = {}
    _app_keyword = None
    current_agent = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_agents()
        return cls._instance

    def _load_agents(self):
        config = Config.from_env()
        self._app_keyword = config.app_keyword.lower()
        session = Session(engine)
        try:
            agents = session.query(Agent).all()
            self._agents = []
            self._agent_map = {}
            self._default_agent = None
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

    def get_agents(self):
        return self._agents

    def find_agent_in_message(self, message: str):
        msg = message.lower()
        for kw, agent in self._agent_map.items():
            search = f"{self._app_keyword} {kw}"
            if search in msg:
                return agent
        return None

    def get_current_agent(self, user_id: str):
        return self.current_agent.get(user_id, self._default_agent)

    def switch(self, message: str, user_id: str) -> bool:
        agent = self.find_agent_in_message(message)
        current_agent = self.current_agent.get(user_id, self._default_agent)
        if agent and (current_agent is None or agent['id'] != current_agent['id']):
            self.current_agent[user_id] = agent
            print(f"Switched to agent: {agent['id']} for user: {user_id}")
            return True
        return False

def get_agent_rooter():
    return AgentRooter()
