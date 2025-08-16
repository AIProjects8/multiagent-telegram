from Agents.agent_base import AgentBase
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config
from Modules.MessageProcessor.message_processor import Message

class DefaultAgent(AgentBase):
    def __init__(self, user_id: str, configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, configuration, questionnaire_answers)
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=self.configuration.get('temperature', 0.7),
            max_tokens=1000
        )
    
    def ask(self, message: Message) -> str:
        system_prompt = "You are a helpful AI assistant responding to user. Provide clear, concise, and helpful responses. Respond in the same language as the user's message."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message.text)
        ]
        
        try:
            response = self.llm.invoke(messages)

            return response.content
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    @property
    def name(self) -> str:
        return "default" 