import re

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