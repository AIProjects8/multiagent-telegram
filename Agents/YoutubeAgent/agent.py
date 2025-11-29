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
        self.graph = self._build_graph(memory)
    
    def _build_graph(self, memory):
        def assistant(state: MessagesState):
            result = self.llm.invoke(state["messages"])
            return {"messages": [result]}
        
        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_edge(START, "assistant")
        builder.add_edge("assistant", END)
        
        return builder.compile(checkpointer=memory)
    
    def _save_message(self, role: str, content: str, session_id: str):
        self.conversation_service.save_message(
            self.user_id,
            self.agent_id,
            role,
            content,
            session_id=session_id
        )
    
    
    async def ask(self, message: Message, send_message: Callable[[str], Any], stream_chunk: Callable[[str, str], Any] = None) -> str:
        youtube_url = extract_youtube_url(message.text)

        if youtube_url:
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
                await send_message(header)
                
                summary_content = await summarize_transcription(
                    transcription, 
                    self.llm, 
                    stream_chunk=stream_chunk
                )
                
                full_summary = header + summary_content
                
                self._save_message('user', message.text, f"{self.user_id}:{self.agent_id}")
                self._save_message('tool', transcription, session_id)
                self._save_message('assistant', full_summary, session_id)
                return self.response(full_summary)
                
            except Exception as e:
                error_msg = self._("Error processing YouTube video: {error}").format(error=str(e))
                self._save_message('assistant', error_msg, session_id)
                return self.response(error_msg)
        else:
            last_session_id = self.conversation_service.get_last_session_id(
                self.user_id,
                self.agent_id
            )
            
            if not last_session_id:
                self._save_message('user', message.text, f"{self.user_id}:{self.agent_id}")
                response = self._("Insert youtube link to generate summary.")
                self._save_message('assistant', response, f"{self.user_id}:{self.agent_id}")
                return self.response(response)
            
            if not extract_youtube_url(last_session_id):
                self._save_message('user', message.text, f"{self.user_id}:{self.agent_id}")
                response = self._("Insert youtube link to generate summary.")
                self._save_message('assistant', response, f"{self.user_id}:{self.agent_id}")
                return self.response(response)
            
            history_messages = self.conversation_service.get_conversation_history(
                self.user_id,
                self.agent_id,
                limit=None,
                exclude_tool_calls=False,
                session_id=last_session_id
            )
            
            if not history_messages:
                self._save_message('user', message.text, f"{self.user_id}:{self.agent_id}")
                response = self._("Insert youtube link to generate summary.")
                self._save_message('assistant', response, f"{self.user_id}:{self.agent_id}")
                return self.response(response)
             
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
            
            messages.append(HumanMessage(content=message.text))
            
            try:
                response_content = await stream_llm_response(self.llm, messages, stream_chunk)
                
                self._save_message('user', message.text, last_session_id)
                self._save_message('assistant', response_content, last_session_id)
                return self.response(response_content)
            except Exception as e:
                error_msg = self._("Error generating response: {error}").format(error=str(e))
                self._save_message('assistant', error_msg, last_session_id)
                return self.response(error_msg)
    
    @property
    def name(self) -> str:
        return "youtube"
