from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from typing import List, Dict, Any, Optional
from SqlDB.conversation_history import ConversationHistoryService
import uuid

class DatabaseBackedChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, user_id: str, agent_id: str):
        self.user_id = user_id
        self.agent_id = agent_id
        self.conversation_service = ConversationHistoryService()
        self._load_existing_history()
    
    def _load_existing_history(self):
        """Load existing conversation history from database"""
        history = self.conversation_service.get_conversation_history(
            self.user_id, 
            self.agent_id, 
            limit=10,
            exclude_tool_calls=True
        )
        
        for msg in reversed(history):
            if msg['role'] == 'user':
                self.messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                self.messages.append(AIMessage(content=msg['content']))
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the store."""
        self.conversation_service.save_message(
            self.user_id, 
            self.agent_id, 
            'user', 
            message
        )
        self.messages.append(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the store."""
        self.conversation_service.save_message(
            self.user_id, 
            self.agent_id, 
            'assistant', 
            message
        )
        self.messages.append(AIMessage(content=message))
    
    def add_tool_call(self, content: str) -> None:
        """Add a tool call to the store (not part of chat history)"""
        self.conversation_service.save_message(
            self.user_id, 
            self.agent_id, 
            'tool', 
            content
        )
    
    def clear(self) -> None:
        """Clear the store."""
        self.messages.clear()
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get all messages."""
        if not hasattr(self, '_messages'):
            self._messages = []
        return self._messages

class ConversationMemoryManager:
    def __init__(self):
        self.histories = {}
    
    def get_chat_history(self, user_id: str, agent_id: str) -> BaseChatMessageHistory:
        """Get or create a chat message history for a user-agent pair"""
        memory_key = f"{user_id}:{agent_id}"
        
        if memory_key not in self.histories:
            self.histories[memory_key] = DatabaseBackedChatMessageHistory(user_id, agent_id)
        
        return self.histories[memory_key]

def get_conversation_memory_manager() -> ConversationMemoryManager:
    return ConversationMemoryManager()
