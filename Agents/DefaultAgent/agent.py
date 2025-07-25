from Agents.agent_base import AgentBase

class DefaultAgent(AgentBase):
    def ask(self, user_id: str, message: str) -> str:
        return f"default agent responding for user {user_id}"
    
    @property
    def name(self) -> str:
        return "default" 