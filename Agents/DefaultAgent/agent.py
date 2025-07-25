from Agents.agent_base import AgentBase
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config
import os

class DefaultAgent(AgentBase):
    def __init__(self):
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=0.7,
            max_tokens=1000
        )
    
    def ask(self, user_id: str, message: str) -> str:
        system_prompt = f"You are a helpful AI assistant responding to user. Provide clear, concise, and helpful responses. Always respond in Polish."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    @property
    def name(self) -> str:
        return "default" 