from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import Config

class Translator:
    def __init__(self):
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=0.1,  # Low temperature for accurate translation
            max_tokens=2000
        )
    
    def translate_to_polish(self, english_text: str) -> str:
        """
        Translate English text to Polish while preserving the exact meaning.
        This is used for translating tool responses (weather, time, etc.) to Polish.
        """
        system_prompt = """You are a professional translator specializing in English to Polish translation.

Your task is to translate the given English text to Polish while:
1. Preserving the EXACT meaning - nothing can be changed or hallucinated
2. Maintaining the same factual information
3. Keeping the same structure and format
4. Using natural, fluent Polish
5. Preserving any numbers, dates, times, and technical terms accurately

Translate the following English text to Polish:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=english_text)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            # Fallback: return original text if translation fails
            print(f"Translation failed: {str(e)}")
            return english_text
