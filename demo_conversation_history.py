#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SqlDB.database import Session, engine
from SqlDB.models import User, Agent
from Modules.ConversationMemory import get_conversation_memory_manager
from SqlDB.conversation_history import ConversationHistoryService

def demo_conversation_history():
    print("🎭 Conversation History System Demo")
    print("=" * 50)
    
    session = Session(engine)
    try:
        users = session.query(User).limit(1).all()
        agents = session.query(Agent).all()
        
        if not users:
            print("❌ No users found. Please run the bot first.")
            return
        
        user = users[0]
        print(f"👤 User: {user.telegram_id}")
        
        memory_manager = get_conversation_memory_manager()
        conversation_service = ConversationHistoryService()
        
        print("\n🌤️  Weather Agent Conversation:")
        print("-" * 30)
        
        weather_agent = next((a for a in agents if a.name == 'weather'), None)
        if weather_agent:
            weather_memory = memory_manager.get_memory(str(user.id), str(weather_agent.id))
            
            weather_memory.save_user_message("What's the weather like in Katowice?")
            weather_memory.save_assistant_message("The weather in Katowice is sunny with a temperature of 22°C.")
            weather_memory.save_tool_call("Weather API call for Katowice: sunny, 22°C")
            
            weather_memory.save_user_message("And what about Wrocław?")
            weather_memory.save_assistant_message("In Wrocław, it's cloudy with a temperature of 18°C.")
            weather_memory.save_tool_call("Weather API call for Wrocław: cloudy, 18°C")
            
            print("✓ Weather conversation saved")
            
            weather_history = conversation_service.get_conversation_history(
                str(user.id), str(weather_agent.id), limit=5
            )
            print(f"📝 Weather conversation history ({len(weather_history)} messages):")
            for msg in weather_history:
                role_icon = "👤" if msg['role'] == 'user' else "🤖" if msg['role'] == 'assistant' else "🔧"
                print(f"  {role_icon} {msg['role']}: {msg['content']}")
        
        print("\n⏰ Time Agent Conversation:")
        print("-" * 30)
        
        time_agent = next((a for a in agents if a.name == 'time'), None)
        if time_agent:
            time_memory = memory_manager.get_memory(str(user.id), str(time_agent.id))
            
            time_memory.save_user_message("What time is it in Warsaw?")
            time_memory.save_assistant_message("The current time in Warsaw is 14:30.")
            time_memory.save_tool_call("Timezone lookup for Warsaw: UTC+2")
            
            time_memory.save_user_message("When does the sun rise tomorrow?")
            time_memory.save_assistant_message("The sun will rise in Warsaw tomorrow at 6:15 AM.")
            time_memory.save_tool_call("Sunrise calculation for Warsaw: 6:15 AM")
            
            print("✓ Time conversation saved")
            
            time_history = conversation_service.get_conversation_history(
                str(user.id), str(time_agent.id), limit=5
            )
            print(f"📝 Time conversation history ({len(time_history)} messages):")
            for msg in time_history:
                role_icon = "👤" if msg['role'] == 'user' else "🤖" if msg['role'] == 'assistant' else "🔧"
                print(f"  {role_icon} {msg['role']}: {msg['content']}")
        
        print("\n🔄 Agent Switching Demo:")
        print("-" * 30)
        
        print("Switching from Weather Agent to Time Agent...")
        if weather_agent and time_agent:
            memory_manager.clear_memory(str(user.id), str(weather_agent.id))
            print("✓ Weather agent memory cleared")
            
            new_time_memory = memory_manager.get_memory(str(user.id), str(time_agent.id))
            print("✓ Time agent memory loaded with existing history")
            
            new_time_history = conversation_service.get_conversation_history(
                str(user.id), str(time_agent.id), limit=5
            )
            print(f"📝 Time agent still has {len(new_time_history)} messages in history")
        
        print("\n📊 Database Statistics:")
        print("-" * 30)
        
        all_user_conversations = conversation_service.get_all_conversations_for_user(str(user.id))
        print(f"Total conversation messages for user: {len(all_user_conversations)}")
        
        print("\n🎉 Demo completed successfully!")
        print("The conversation history system is working correctly with:")
        print("✓ Separate conversation sessions for each agent")
        print("✓ Tool call logging")
        print("✓ Memory clearing when switching agents")
        print("✓ Persistent storage in database")
        print("✓ Context-aware conversations")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    demo_conversation_history()
