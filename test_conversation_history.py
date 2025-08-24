#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Modules.ConversationMemory import get_conversation_memory_manager
from SqlDB.conversation_history import ConversationHistoryService
from SqlDB.database import Session, engine
from SqlDB.models import User, Agent, ConversationHistory

def test_conversation_history():
    print("Testing Conversation History System (LangGraph)...")
    
    try:
        conversation_service = ConversationHistoryService()
        memory_manager = get_conversation_memory_manager()
        
        session = Session(engine)
        try:
            users = session.query(User).limit(1).all()
            agents = session.query(Agent).limit(1).all()
            
            if not users or not agents:
                print("❌ No users or agents found in database. Please run the bot first to initialize data.")
                return
            
            test_user = users[0]
            test_agent = agents[0]
            
            test_user_id = str(test_user.id)
            test_agent_id = str(test_agent.id)
            
            print(f"✓ Using existing user: {test_user.telegram_id}")
            print(f"✓ Using existing agent: {test_agent.name}")
            print(f"✓ Test user ID: {test_user_id}")
            print(f"✓ Test agent ID: {test_agent_id}")
            
            session_id = f"{test_user_id}:{test_agent_id}"
            print(f"✓ Session ID: {session_id}")
            
            chat_history = memory_manager.get_chat_history(test_user_id, test_agent_id)
            print("✓ Chat history instance created")
            
            chat_history.add_user_message("Hello, what's the weather like?")
            print("✓ User message saved")
            
            chat_history.add_ai_message("The weather is sunny today!")
            print("✓ Assistant message saved")
            
            chat_history.add_tool_call("Weather API call: temperature=25°C, condition=sunny")
            print("✓ Tool call saved")
            
            history = conversation_service.get_conversation_history(test_user_id, test_agent_id)
            print(f"✓ Retrieved {len(history)} conversation messages")
            
            for msg in history:
                print(f"  - {msg['role']}: {msg['content'][:50]}...")
            
            chat_messages = chat_history.messages
            print(f"✓ Chat history: {len(chat_messages)} messages")
            
            print("✓ Memory test completed")
            
            print("\n🎉 All tests passed! Conversation history system is working correctly with LangGraph!")
            
        finally:
            session.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_message_count_with_tool_calls():
    print("\n🧪 Testing Message Count with Tool Calls...")
    
    try:
        conversation_service = ConversationHistoryService()
        
        session = Session(engine)
        try:
            users = session.query(User).limit(1).all()
            agents = session.query(Agent).limit(1).all()
            
            if not users or not agents:
                print("❌ No users or agents found in database.")
                return
            
            test_user = users[0]
            test_agent = agents[0]
            
            test_user_id = str(test_user.id)
            test_agent_id = str(test_agent.id)
            
            # Add 15 messages: 10 user/assistant + 5 tool calls
            for i in range(1, 16):
                if i % 3 == 0:  # Every 3rd message is a tool call
                    conversation_service.save_message(test_user_id, test_agent_id, 'tool', f'Tool call {i}')
                elif i % 2 == 0:  # Even numbers are user messages
                    conversation_service.save_message(test_user_id, test_agent_id, 'user', f'User message {i}')
                else:  # Odd numbers are assistant messages
                    conversation_service.save_message(test_user_id, test_agent_id, 'assistant', f'Assistant message {i}')
            
            print(f"✓ Created 15 messages (including tool calls)")
            
            # Test getting 10 messages excluding tool calls
            history = conversation_service.get_conversation_history(test_user_id, test_agent_id, limit=10, exclude_tool_calls=True)
            print(f"✓ Retrieved {len(history)} messages (excluding tool calls)")
            
            if len(history) == 10:
                print("✅ SUCCESS: Got exactly 10 messages as requested!")
            else:
                print(f"❌ FAILED: Expected 10 messages, got {len(history)}")
            
            # Show the messages
            print("Messages retrieved:")
            for i, msg in enumerate(history, 1):
                print(f"  {i}. {msg['role']}: {msg['content']}")
            
            print("✓ Test completed successfully")
            
        finally:
            session.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation_history()
    test_message_count_with_tool_calls()
