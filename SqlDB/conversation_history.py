from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import engine
from .models import ConversationHistory
from typing import List
import uuid

class ConversationHistoryService:
    def __init__(self):
        self.engine = engine
    
    def _get_session(self) -> Session:
        return Session(self.engine)
    
    def save_message(self, user_id: str, agent_id: str, role: str, content: str, session_id: str = None) -> str:
        session = self._get_session()
        try:
            if session_id is None:
                session_id = f"{user_id}:{agent_id}"
            
            conversation_message = ConversationHistory(
                user_id=uuid.UUID(user_id),
                agent_id=uuid.UUID(agent_id),
                role=role,
                content=content,
                session_id=session_id
            )
            
            session.add(conversation_message)
            session.commit()
            
            return str(conversation_message.id)
        finally:
            session.close()
    
    def get_conversation_history(self, user_id: str, agent_id: str, limit: int = 10, exclude_tool_calls: bool = True, session_id: str = None) -> List[dict]:
        session = self._get_session()
        try:
            query = session.query(ConversationHistory).filter(
                ConversationHistory.user_id == uuid.UUID(user_id),
                ConversationHistory.agent_id == uuid.UUID(agent_id)
            )
            
            if session_id is not None:
                query = query.filter(ConversationHistory.session_id == session_id)
            
            if exclude_tool_calls:
                query = query.filter(ConversationHistory.role != 'tool')
            
            messages = query.order_by(desc(ConversationHistory.timestamp)).limit(limit).all()
            
            return [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in messages
            ]
        finally:
            session.close()
