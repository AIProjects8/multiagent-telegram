from Agents.agent_base import AgentBase

class WeatherAgent(AgentBase):
    def ask(self, user_id: str, message: str) -> str:
        return f"weather agent responding for user {user_id}"
    
    @property
    def name(self) -> str:
        return "weather" 