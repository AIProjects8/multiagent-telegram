from abc import ABC, abstractmethod
from typing import Dict, Any

class AgentBase(ABC):
    """Base interface for all agents in the system"""
    
    @abstractmethod
    def ask(self, user_id: str, message: str) -> str:
        """Process a user message and return a response"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name"""
        pass
