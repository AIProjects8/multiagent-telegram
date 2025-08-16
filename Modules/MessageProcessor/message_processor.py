import re
from dataclasses import dataclass

@dataclass
class Message:
    text: str
    language: str

class MessageProcessor:
    @staticmethod
    def clean_message(message: str) -> str:
        cleaned = message.strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    @staticmethod
    def should_process_message(message: str) -> bool:
        words = message.split()
        if len(words) == 2 and words[0].lower() == "agent":
            return False
        return True
    
    @staticmethod
    def create_message(text: str, language: str) -> Message:
        """
        Create a Message object with cleaned text and language code.
        """
        cleaned_text = MessageProcessor.clean_message(text)
        return Message(text=cleaned_text, language=language) 