import importlib
import os
from typing import Dict, Type
from Agents.agent_base import AgentBase

class AgentFactory:    
    _agents_cache: Dict[str, Type[AgentBase]] = {}
    _agents_path = "Agents"
    
    @classmethod
    def get_agent_class(cls, agent_name: str) -> Type[AgentBase]:
        if agent_name in cls._agents_cache:
            return cls._agents_cache[agent_name]
        
        agent_folder = f"{agent_name.capitalize()}Agent"
        agent_file = "agent.py"
        agent_class_name = f"{agent_name.capitalize()}Agent"
        
        module_path = f"{cls._agents_path}.{agent_folder}.{agent_file.replace('.py', '')}"
        
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, agent_class_name)
            
            if not issubclass(agent_class, AgentBase):
                raise ValueError(f"Agent class {agent_class_name} must inherit from BaseAgent")
            
            cls._agents_cache[agent_name] = agent_class
            return agent_class
            
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load agent {agent_name}: {str(e)}")
    
    @classmethod
    def create_agent(cls, agent_name: str) -> AgentBase:
        agent_class = cls.get_agent_class(agent_name)
        return agent_class()
    
    @classmethod
    def get_available_agents(cls) -> list[str]:
        agents = []
        if os.path.exists(cls._agents_path):
            for item in os.listdir(cls._agents_path):
                if item.endswith("Agent") and os.path.isdir(os.path.join(cls._agents_path, item)):
                    agent_name = item.replace("Agent", "")
                    agents.append(agent_name)
        return agents 