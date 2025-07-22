import openai
from config import Config

class OpenAIClient:
    _instance = None
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if OpenAIClient._client is None:
            config = Config.from_env()
            OpenAIClient._client = openai.OpenAI(api_key=config.openai_api_key)

    @property
    def client(self):
        return self._client
