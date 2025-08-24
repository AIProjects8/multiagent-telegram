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
    langsmith_api_key: str
    open_weather_map_api_key: str
    voice_response: bool
    gpt_model: str
    allowed_user_ids: list[int]
    app_keyword: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    time_zone: str

    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()
        
        allowed_user_ids_str = os.getenv("ALLOWED_USER_IDS", "")
        allowed_user_ids = [int(uid.strip()) for uid in allowed_user_ids_str.split(",") if uid.strip()]
        
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_API_KEY"),
            bot_username=os.getenv("BOT_USERNAME"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
            open_weather_map_api_key=os.getenv("OPEN_WEATHER_MAP_API_KEY"),
            voice_response=os.getenv("VOICE_RESPONSE"),
            gpt_model=os.getenv("GPT_MODEL"),
            allowed_user_ids=allowed_user_ids,
            app_keyword=os.getenv("APP_KEYWORD"),
            postgres_user=os.getenv("POSTGRES_USER", "postgres"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            postgres_db=os.getenv("POSTGRES_DB", "multiagent_bot"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=os.getenv("POSTGRES_PORT", "5432"),
            time_zone=os.getenv("TIME_ZONE", "UTC")
    )

    def validate(self) -> None:
        missing_vars = []
        
        if not self.telegram_bot_token:
            missing_vars.append("TELEGRAM_BOT_API_KEY")
        if not self.bot_username:
            missing_vars.append("BOT_USERNAME")
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
        if not self.langsmith_api_key:
            missing_vars.append("LANGSMITH_API_KEY")
        if not self.open_weather_map_api_key:
            missing_vars.append("OPEN_WEATHER_MAP_API_KEY")
        if not self.voice_response:
            missing_vars.append("VOICE_RESPONSE")
        if not self.gpt_model:
            missing_vars.append("GPT_MODEL")
        if not self.allowed_user_ids:
            missing_vars.append("ALLOWED_USER_IDS")
        if not self.app_keyword:
            missing_vars.append("APP_KEYWORD")
        if not self.postgres_user:
            missing_vars.append("POSTGRES_USER")
        if not self.postgres_password:
            missing_vars.append("POSTGRES_PASSWORD")
        if not self.postgres_db:
            missing_vars.append("POSTGRES_DB")
        if not self.postgres_host:
            missing_vars.append("POSTGRES_HOST")
        if not self.postgres_port:
            missing_vars.append("POSTGRES_PORT")
        if not self.time_zone:
            missing_vars.append("TIME_ZONE")
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 