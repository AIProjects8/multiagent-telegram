from Agents.agent_base import AgentBase
from Modules.MessageProcessor.message_processor import Message
from SqlDB.conversation_history import ConversationHistoryService
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from config import Config
from typing import Any, Callable
from .tools import add, subtract, multiply, divide, pow, sqrt

class CalculatorAgent(AgentBase):
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.conversation_service = ConversationHistoryService()
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=self.agent_configuration.get('temperature', 0.2)
        )
        
        tools = [add, subtract, multiply, divide, pow, sqrt]
        print(f"Tools registered: {[tool.name for tool in tools]}")
        print(f"Model: {self.config.gpt_model}")
        for tool in tools:
            print(f"Tool {tool.name}: {tool.description}")
        
        self.llm_with_tools = self.llm.bind_tools(tools)
        
        memory = MemorySaver()
        self.react_graph = self._build_graph(tools, memory)
    
    def _build_graph(self, tools, memory):
        def assistant(state: MessagesState):
            history = self.conversation_service.get_conversation_history(
                self.user_id,
                self.agent_id,
                limit=5,
                exclude_tool_calls=True
            )
            
            history.reverse()
            
            system_msg = SystemMessage(content="You are a calculator. When asked to perform a calculation, you MUST use the available tools. Available tools: add (for addition), subtract (for subtraction), multiply (for multiplication), divide (for division), pow (for exponentiation), sqrt (for square root). After using tools and getting results, respond with ONLY the final numerical result - no explanations, no text, just the number.")
            messages = [system_msg]
            
            for msg in history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
            
            messages.extend(state["messages"])
            
            result = self.llm_with_tools.invoke(messages)
            
            print(f"LLM response type: {type(result)}")
            print(f"LLM response content: {result.content if hasattr(result, 'content') else 'N/A'}")
            print(f"Has tool_calls attribute: {hasattr(result, 'tool_calls')}")
            if hasattr(result, 'tool_calls'):
                print(f"Tool calls: {result.tool_calls}")
                if result.tool_calls:
                    print(f"Tool calls detected: {result.tool_calls}")
                else:
                    print("WARNING: No tool calls in response!")
            else:
                print("WARNING: Response doesn't have tool_calls attribute!")
            
            return {"messages": [result]}
        
        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        
        return builder.compile(checkpointer=memory)
    
    def _save_message(self, role: str, content: str, session_id: str):
        self.conversation_service.save_message(
            self.user_id,
            self.agent_id,
            role,
            content,
            session_id=session_id
        )
    
    def _format_tool_usage(self, messages: list) -> str:
        tool_info = []
        tool_results = {}
        
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results[msg.tool_call_id] = msg.content
            
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    tool_args = tool_call.get('args', {})
                    tool_call_id = tool_call.get('id', '')
                    
                    args_str = ' '.join([f"{k} = {v}" for k, v in tool_args.items()])
                    tool_info.append(f"{tool_name} {args_str}")
                    
                    if tool_call_id in tool_results:
                        result = tool_results[tool_call_id]
                        tool_info.append(f"result {result}")
        
        if tool_info:
            return '\n'.join(tool_info) + '\n\n'
        return ''
    
    async def ask(self, message: Message, send_message: Callable[[str], Any]) -> str:
        session_id = f"{self.user_id}:{self.agent_id}"
        
        try:
            config = {"configurable": {"thread_id": session_id}}
            messages = [HumanMessage(content=message.text)]
            
            print(f"Invoking react graph with message: {message.text}")
            result = self.react_graph.invoke({"messages": messages}, config)
            
            print(f"Graph result messages count: {len(result['messages'])}")
            for i, msg in enumerate(result['messages']):
                print(f"Message {i}: type={type(msg).__name__}, has tool_calls={hasattr(msg, 'tool_calls')}")
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"  Tool calls: {msg.tool_calls}")
            
            last_message = result['messages'][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            import re
            numbers = re.findall(r'-?\d+\.?\d*', response_content)
            if numbers:
                try:
                    num_value = float(numbers[-1])
                    if num_value.is_integer():
                        response_content = str(int(num_value))
                    else:
                        response_content = f"{num_value:.10f}".rstrip('0').rstrip('.')
                except ValueError:
                    response_content = numbers[-1]
            
            self._save_message('user', message.text, session_id)
            self._save_message('assistant', response_content, session_id)
            
            for msg in result['messages']:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        self._save_message('tool', f"{tool_call['name']}({tool_call.get('args', {})})", session_id)
            
            return self.response(response_content)
        except Exception as e:
            import traceback
            print(f"Error in ask: {e}")
            traceback.print_exc()
            error_msg = self._("Error processing calculation: {error}").format(error=str(e))
            self._save_message('user', message.text, session_id)
            self._save_message('assistant', error_msg, session_id)
            return self.response(error_msg)
    
    @property
    def name(self) -> str:
        return "calculator"

