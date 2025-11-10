from Agents.agent_base import AgentBase
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import Config
from Modules.MessageProcessor.message_processor import Message

class DefaultAgent(AgentBase):
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=self.agent_configuration.get('temperature', 0.7),
            max_tokens=1000
        )
    
    def ask(self, message: Message) -> str:
        system_prompt = "You are a helpful AI assistant responding to user. Provide clear, concise, and helpful responses. Respond in the same language as the user's message."
        
        chat_history = self._get_chat_history()
        messages = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=message.text)]
        
        try:
            response = self.llm.invoke(messages)
            response_content = response.content
            
            if response_content is '':
                raise Exception("Response content is empty")
            
            self._save_user_message(message)
            self._save_assistant_message(response_content)
            return response_content
                
        except Exception as e:
            error_response = self._("Sorry, I encountered an error: {error}").format(error=str(e))
            return error_response
    
    @property
    def name(self) -> str:
        return "default" 