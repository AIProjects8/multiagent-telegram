# Conversation History System

This document describes the conversation history system implemented for the multi-agent Telegram bot using **LangGraph memory** - the modern, recommended approach for LangChain applications.

## Overview

The conversation history system allows each agent to maintain context-aware conversations with users by storing and retrieving conversation history from a PostgreSQL database. Each user-agent combination has its own conversation session, and the history is automatically managed when switching between agents.

**Note**: This system uses the modern LangGraph memory approach as recommended in the [LangChain migration guide](https://python.langchain.com/docs/versions/migrating_memory/), replacing the deprecated `ConversationBufferMemory` and `ConversationBufferWindowMemory`.

## Architecture

### Database Schema

The system uses a new `conversation_history` table with the following structure:

```sql
CREATE TABLE conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    agent_id UUID NOT NULL REFERENCES agents(id),
    role VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'tool'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255) NOT NULL
);
```

**Note**: The old `conversations` table has been removed as it's no longer needed.

### Session Management

- **Session ID Format**: `{user_id}:{agent_id}`
- Each user-agent combination has a unique session
- When switching agents, the previous agent's conversation history is cleared from memory
- History is preserved in the database for future reference

### Memory Types

The system now uses **LangGraph memory** components:

1. **`BaseChatMessageHistory`**: Modern interface for managing chat message history
2. **`RunnableWithMessageHistory`**: Ready for integration with LangGraph applications
3. **Database-backed persistence**: PostgreSQL storage for conversation history

## Implementation Details

### Core Components

1. **ConversationHistoryService** (`SqlDB/conversation_history.py`)
   - Handles database operations for conversation history
   - Provides methods to save, retrieve, and filter messages

2. **DatabaseBackedChatMessageHistory** (`Modules/ConversationMemory/conversation_memory.py`)
   - Implements `BaseChatMessageHistory` interface
   - Integrates with database for persistent storage
   - Automatically loads existing history when initialized

3. **ConversationMemoryManager** (`Modules/ConversationMemory/conversation_memory.py`)
   - Manages chat history instances for different user-agent combinations
   - Provides clean interface for accessing conversation history

### Agent Integration

All agents now inherit conversation history functionality from `AgentBase`:

```python
class WeatherAgent(AgentBase):
    def ask(self, message: Message) -> str:
        self._save_user_message(message)  # Save user message
        response = self._get_response(message)
        self._save_assistant_message(response)  # Save assistant response
        return response
    
    def _get_response(self, message: Message) -> str:
        # Get conversation history for context
        chat_history = self._get_chat_history()
        
        # Use history in LLM calls
        messages = [system_message] + chat_history + [user_message]
        llm_response = self.llm.invoke(messages)
        
        # Save tool calls if any
        self._save_tool_call(f"Weather API call: {weather_data}")
        
        return response
```

## Usage Examples

### Basic Conversation Flow

1. **User sends message**: Message is automatically saved to conversation history
2. **Agent processes message**: Agent retrieves conversation history for context
3. **LLM generates response**: Response considers previous conversation context
4. **Response saved**: Assistant response is saved to conversation history
5. **Tool calls logged**: Any API calls or tool usage is logged separately

### Agent Switching

```python
# When user types "agent weather"
# Previous agent's memory is cleared
# New agent loads its conversation history
# User can continue conversation with context
```

### Retrieving History

```python
# Get last 10 messages (excluding tool calls)
history = conversation_service.get_conversation_history(
    user_id, 
    agent_id, 
    limit=10, 
    exclude_tool_calls=True
)
```

**Important Note on Message Counting**: When `exclude_tool_calls=True` is set, the method ensures you get exactly the requested number of messages. For example, if you request 10 messages and there are 15 total messages (including 5 tool calls), you'll get exactly 10 user/assistant messages, not 7. The tool calls are filtered out at the database level using SQL's `LIMIT` clause, ensuring efficient querying and consistent message counts for your LLM context.

**Note**: The conversation history system is designed to be simple and focused. It only provides methods for saving messages and retrieving conversation history. If you need to clear conversations or get all conversations for a user, you can do that directly in the database.

## Configuration

### Memory Settings

- **Default Window Size**: 10 messages
- **Memory Type**: LangGraph `BaseChatMessageHistory` (modern approach)
- **Tool Call Storage**: Separate storage for API calls and tool usage

### Database Integration

The `conversation_history` table is now part of the standard table initialization process:

```python
# In database.py
required_tables = ['users', 'agents', 'agent_items', 'scheduler', 'conversation_history']
missing_tables = [table for table in required_tables if table not in existing_tables]

if missing_tables:
    Base.metadata.create_all(bind=engine)  # Creates conversation_history along with other missing tables
```

## Setup

The conversation history system is automatically initialized when the database is set up:

1. **Database Initialization**: The `conversation_history` table is included in the `required_tables` list and created automatically by SQLAlchemy when missing
2. **No Migration Required**: The system follows the exact same pattern as other database models (User, Agent, Scheduler, etc.)
3. **Automatic Setup**: Simply run your existing database initialization code - the table is created automatically along with other missing tables

## Benefits

1. **Context Awareness**: Agents can understand conversation context
2. **Improved Responses**: Better responses based on conversation history
3. **Session Isolation**: Each agent maintains separate conversation context
4. **Tool Call Logging**: Track API usage and tool calls separately
5. **Scalability**: Database-backed storage for large conversation volumes
6. **Performance**: Efficient indexing and memory management
7. **Modern Architecture**: Uses LangGraph memory as recommended by LangChain
8. **Future-Proof**: Ready for LangGraph integration and advanced memory features

## Limitations

1. **Memory Size**: Limited to last 10 messages by default
2. **Database Storage**: Requires additional database space
3. **Initialization**: Slight delay when loading conversation history

## Future Enhancements

1. **LangGraph Integration**: Ready for advanced graph-based memory management
2. **Configurable Memory Size**: Allow agents to configure their own memory limits
3. **Advanced Filtering**: More sophisticated conversation filtering options
4. **Analytics**: Conversation analytics and insights
5. **Export**: Export conversation history for analysis
6. **Vector Search**: Semantic search through conversation history
7. **Memory Summarization**: Automatic conversation summarization for long histories
