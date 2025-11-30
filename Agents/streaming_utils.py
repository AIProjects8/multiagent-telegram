from typing import Any, Callable
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage


async def stream_llm_response(
    llm: ChatOpenAI,
    messages: list[BaseMessage],
    stream_chunk: Callable[[str, str], Any],
    initial_text: str = ""
) -> str:
    accumulated = initial_text
    response_content = ""
    
    async for chunk in llm.astream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            accumulated += chunk.content
            await stream_chunk(chunk.content, accumulated)
            response_content = accumulated
    
    if not response_content:
        response = llm.invoke(messages)
        response_content = response.content
        if initial_text:
            accumulated = initial_text + response_content
        else:
            accumulated = response_content
        await stream_chunk(response_content, accumulated)
        response_content = accumulated
    
    return response_content

