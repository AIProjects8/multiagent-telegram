from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AgentBase(ABC):
    """Base interface for all agents in the system"""
    
    def __init__(self, user_id: str, configuration: Dict[str, Any], questionnaire_answers: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.configuration = configuration
        self.questionnaire_answers = questionnaire_answers or {}
    
    @abstractmethod
    def ask(self, message: str) -> str:
        """Process a user message and return a response"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name"""
        pass

