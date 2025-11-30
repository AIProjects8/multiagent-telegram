from Agents.agent_base import AgentBase
from Agents.streaming_utils import stream_llm_response
from Modules.MessageProcessor.message_processor import Message
from SqlDB.conversation_history import ConversationHistoryService
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from config import Config
from typing import Any, Callable
from .youtube_tools import (
    extract_youtube_url,
    extract_video_id,
    get_video_metadata,
    fetch_transcription
)
from .transcription_tools import (
    summarize_transcription
)


class YoutubeAgentState(MessagesState):
    message_text: str
    youtube_url: str | None
    transcription: str | None
    summary: str | None
    session_id: str | None
    has_transcription: bool
    response: str | None

class YoutubeAgent(AgentBase):
    def __init__(self, user_id: str, agent_id: str, agent_configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, agent_id, agent_configuration, questionnaire_answers)
        self.conversation_service = ConversationHistoryService()
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=self.agent_configuration.get('temperature', 0.2)
        )
        memory = MemorySaver()
        self._send_message = None
        self._stream_chunk = None
        self.graph = None
    
    def _build_graph(self, memory, send_message, stream_chunk):
        async def check_message_type(state: YoutubeAgentState):
            message_text = state["message_text"]
            youtube_url = extract_youtube_url(message_text)
            return {
                "youtube_url": youtube_url,
                "messages": [HumanMessage(content=message_text)]
            }
        
        async def handle_youtube_url(state: YoutubeAgentState):
            youtube_url = state["youtube_url"]
            session_id = youtube_url
            
            try:
                await send_message(self._("Youtube link is correct. Downloading transcription."))
                
                video_id = extract_video_id(youtube_url)
                user_language = self._get_user_language()
                transcription = None
                
                try:
                    transcription = fetch_transcription(youtube_url, language=user_language)
                except Exception:
                    if user_language != 'en':
                        await send_message(self._("Transcription not available in {language}. Trying English...").format(language=user_language))
                        try:
                            transcription = fetch_transcription(youtube_url, language='en')
                        except Exception:
                            await send_message(self._("Transcription not available in English."))
                            raise
                    else:
                        await send_message(self._("Transcription not available in English."))
                        raise
                
                await send_message(self._("Transcription downloaded. Generating summary."))
                
                video_title, video_date = get_video_metadata(video_id)
                header = f"""{self._("Title")}: {video_title}
{self._("Publication date")}: {video_date}

"""

                summary_content = await summarize_transcription(
                    transcription,
                    self.llm,
                    stream_chunk=stream_chunk
                )
                
                full_summary = header + summary_content
                
                self._save_message('user', state["message_text"], f"{self.user_id}:{self.agent_id}")
                self._save_message('tool', transcription, session_id)
                self._save_message('assistant', full_summary, session_id)
                
                return {
                    "transcription": transcription,
                    "summary": full_summary,
                    "session_id": session_id,
                    "response": full_summary,
                    "messages": [AIMessage(content=full_summary)]
                }
            except Exception as e:
                error_msg = self._("Error processing YouTube video: {error}").format(error=str(e))
                self._save_message('assistant', error_msg, session_id)
                return {
                    "response": error_msg,
                    "messages": [AIMessage(content=error_msg)]
                }
        
        async def check_previous_transcription(state: YoutubeAgentState):
            last_session_id = self.conversation_service.get_last_session_id(
                self.user_id,
                self.agent_id
            )
            
            if not last_session_id or not extract_youtube_url(last_session_id):
                return {"session_id": None, "has_transcription": False}
            
            
            history_messages = self.conversation_service.get_conversation_history(
                self.user_id,
                self.agent_id,
                limit=None,
                exclude_tool_calls=False,
                session_id=last_session_id
            )
            
            has_transcription = bool(history_messages)
            return {
                "session_id": last_session_id if has_transcription else None,
                "has_transcription": has_transcription
            }
        
        async def request_youtube_url(state: YoutubeAgentState):
            response = self._("Insert youtube link to generate summary.")
            self._save_message('user', state["message_text"], f"{self.user_id}:{self.agent_id}")
            self._save_message('assistant', response, f"{self.user_id}:{self.agent_id}")
            return {
                "response": response,
                "messages": [AIMessage(content=response)]
            }
        
        async def answer_question(state: YoutubeAgentState):
            session_id = state["session_id"]
            
            history_messages = self.conversation_service.get_conversation_history(
                self.user_id,
                self.agent_id,
                limit=None,
                exclude_tool_calls=False,
                session_id=session_id
            )
            
            history_messages.reverse()
            
            system_prompt = self._("You are a helpful assistant. Answer based on the conversation history and current message. Be straight to the point without long explanations. If the user wants more details, they will ask.")
            
            messages = [SystemMessage(content=system_prompt)]
            
            for msg in history_messages:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
                elif msg['role'] == 'tool':
                    messages.append(SystemMessage(content=f"Full video transcription:\n{msg['content']}"))
            
            messages.append(HumanMessage(content=state["message_text"]))
            
            try:
                response_content = await stream_llm_response(self.llm, messages, stream_chunk)
                
                self._save_message('user', state["message_text"], session_id)
                self._save_message('assistant', response_content, session_id)
                
                return {
                    "response": response_content,
                    "messages": [AIMessage(content=response_content)]
                }
            except Exception as e:
                error_msg = self._("Error generating response: {error}").format(error=str(e))
                self._save_message('assistant', error_msg, session_id)
                return {
                    "response": error_msg,
                    "messages": [AIMessage(content=error_msg)]
                }
        
        def route_after_check(state: YoutubeAgentState) -> str:
            if state.get("youtube_url"):
                return "handle_youtube_url"
            return "check_previous_transcription"
        
        def route_after_check_transcription(state: YoutubeAgentState) -> str:
            if state.get("has_transcription"):
                return "answer_question"
            return "request_youtube_url"
        
        builder = StateGraph(YoutubeAgentState)
        builder.add_node("check_message_type", check_message_type)
        builder.add_node("handle_youtube_url", handle_youtube_url)
        builder.add_node("check_previous_transcription", check_previous_transcription)
        builder.add_node("request_youtube_url", request_youtube_url)
        builder.add_node("answer_question", answer_question)
        
        builder.add_edge(START, "check_message_type")
        builder.add_conditional_edges(
            "check_message_type",
            route_after_check,
            {
                "handle_youtube_url": "handle_youtube_url",
                "check_previous_transcription": "check_previous_transcription"
            }
        )
        builder.add_edge("handle_youtube_url", END)
        builder.add_conditional_edges(
            "check_previous_transcription",
            route_after_check_transcription,
            {
                "answer_question": "answer_question",
                "request_youtube_url": "request_youtube_url"
            }
        )
        builder.add_edge("request_youtube_url", END)
        builder.add_edge("answer_question", END)
        
        return builder.compile(checkpointer=memory)
    
    def _build_graph_with_callbacks(self, memory, send_message, stream_chunk):
        return self._build_graph(memory, send_message, stream_chunk)
    
    def _save_message(self, role: str, content: str, session_id: str):
        self.conversation_service.save_message(
            self.user_id,
            self.agent_id,
            role,
            content,
            session_id=session_id
        )
    
    
    async def ask(self, message: Message, send_message: Callable[[str], Any], stream_chunk: Callable[[str, str], Any] = None) -> str:
        memory = MemorySaver()
        graph = self._build_graph(memory, send_message, stream_chunk)
        config = {"configurable": {"thread_id": f"{self.user_id}:{self.agent_id}"}}
        
        initial_state = {
            "messages": [],
            "message_text": message.text,
            "youtube_url": None,
            "transcription": None,
            "summary": None,
            "session_id": None,
            "has_transcription": False,
            "response": None
        }
        
        result = await graph.ainvoke(initial_state, config)
        return self.response(result.get("response", ""))
    
    @property
    def name(self) -> str:
        return "youtube"
