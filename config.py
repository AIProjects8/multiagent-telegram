from dataclasses import dataclass
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

@dataclass
class Config:
    telegram_bot_token: str
    bot_username: str
    openai_api_key: str
    voice_response: bool
    gpt_model: str
    allowed_user_ids: list[int]

    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()
        
        allowed_user_ids_str = os.getenv("ALLOWED_USER_IDS", "")
        allowed_user_ids = [int(uid.strip()) for uid in allowed_user_ids_str.split(",") if uid.strip()]
        
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_API_KEY"),
            bot_username=os.getenv("BOT_USERNAME"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            voice_response=os.getenv("VOICE_RESPONSE"),
            gpt_model=os.getenv("GPT_MODEL"),
            allowed_user_ids=allowed_user_ids
        )

    def validate(self) -> None:
        missing_vars = []
        
        if not self.telegram_bot_token:
            missing_vars.append("TELEGRAM_BOT_API_KEY")
        if not self.bot_username:
            missing_vars.append("BOT_USERNAME")
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
        if not self.voice_response:
            missing_vars.append("VOICE_RESPONSE")
        if not self.gpt_model:
            missing_vars.append("GPT_MODEL")
        if not self.allowed_user_ids:
            missing_vars.append("ALLOWED_USER_IDS")
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 