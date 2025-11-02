from Agents.agent_base import AgentBase
from Modules.MessageProcessor.message_processor import Message
from SqlDB.conversation_history import ConversationHistoryService
from datetime import datetime

class YoutubeAgent(AgentBase):
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.conversation_service = ConversationHistoryService()
    
    def _get_session_id(self) -> str:
        now = datetime.now()
        return now.strftime("%d-%m-%Y-%H")
    
    def _save_message(self, role: str, content: str):
        session_id = self._get_session_id()
        self.conversation_service.save_message(
            self.user_id,
            self.agent_id,
            role,
            content,
            session_id=session_id
        )
    
    def ask(self, message: Message) -> str:
        self._save_message('user', message.text)
        
        session_id = self._get_session_id()
        history_messages = self.conversation_service.get_conversation_history(
            self.user_id,
            self.agent_id,
            limit=2,
            exclude_tool_calls=True,
            session_id=session_id
        )
        
        last_assistant_message = None
        for msg in history_messages:
            if msg['role'] == 'assistant':
                last_assistant_message = msg['content']
                break
        
        if last_assistant_message:
            response = last_assistant_message + message.text
        else:
            response = message.text
        
        self._save_message('assistant', response)
        return response
    
    @property
    def name(self) -> str:
        return "youtube"

