from sqlalchemy.orm import Session
from datetime import time
from SqlDB.models import Agent, User, AgentItem, Scheduler

def init_user(db: Session):
    existing_user = db.query(User).filter(User.telegram_id == 8133073522).first()
    
    if not existing_user:
        user = User(
            telegram_id=8133073522,
            name="Test User"
        )
        
        db.add(user)
        db.commit()
        print("User created successfully")
    else:
        print("User already exists")

def init_weather_agent(db: Session):
    existing_agent = db.query(Agent).filter(Agent.name == 'weather').first()
    
    if not existing_agent:
        weather_config = [
            {
                "name": "city_name",
                "type": "string"
            },
            {
                "name": "city_lat",
                "type": "float"
            },
            {
                "name": "city_lon",
                "type": "float"
            },
            {
                "name": "scheduler_active",
                "type": "bool"
            }
        ]
        
        weather_agent = Agent(
            name='weather',
            keywords='pogoda,pogodowy,pogodny,pogodę,pogode',
            configuration=weather_config
        )
        
        db.add(weather_agent)
        db.commit()
        print("Weather agent created successfully")
    else:
        print("Weather agent already exists")

def init_agent_item(db: Session):
    user = db.query(User).filter(User.telegram_id == 8133073522).first()
    if not user:
        print("User with telegram_id 8133073522 not found")
        return
    
    weather_agent = db.query(Agent).filter(Agent.name == 'weather').first()
    if not weather_agent:
        print("Weather agent not found")
        return
    
    existing_item = db.query(AgentItem).filter(
        AgentItem.user_id == user.id,
        AgentItem.agent_id == weather_agent.id
    ).first()
    
    if existing_item:
        print("Agent item already exists for this user and agent")
        return
    
    questionnaire_answers = {
        "city_name": "Katowice",
        "city_lat": 50.2644,
        "city_lon": 19.0232,
        "scheduler_active": True
    }
    
    agent_item = AgentItem(
        user_id=user.id,
        agent_id=weather_agent.id,
        questionnaire_answers=questionnaire_answers,
        questionnaire_completed=True
    )
    
    db.add(agent_item)
    db.commit()
    print(f"Agent item created successfully with ID: {agent_item.id}")

def init_scheduler(db: Session):
    user = db.query(User).filter(User.telegram_id == 8133073522).first()
    if not user:
        print("User with telegram_id 8133073522 not found")
        return
    
    weather_agent = db.query(Agent).filter(Agent.name == 'weather').first()
    if not weather_agent:
        print("Weather agent not found")
        return
    
    existing_scheduler = db.query(Scheduler).filter(
        Scheduler.user_id == user.id,
        Scheduler.agent_id == weather_agent.id
    ).first()
    
    if existing_scheduler:
        print("Scheduler already exists for this user and agent")
        return
    
    scheduler = Scheduler(
        user_id=user.id,
        agent_id=weather_agent.id,
        time=time(7, 0)
    )
    
    db.add(scheduler)
    db.commit()
    print(f"Scheduler created successfully for 7:00 AM with ID: {scheduler.id}") 