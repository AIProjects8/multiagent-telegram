from sqlalchemy.orm import Session
from datetime import time
from SqlDB.models import Agent, User, AgentItem, Scheduler

def init_user(db: Session):
    existing_user = db.query(User).filter(User.telegram_id == 8133073522).first()
    
    if not existing_user:
        user = User(
            telegram_id=8133073522,
            name="Test User",
            chat_id=8133073522
        )
        
        db.add(user)
        db.commit()
        print("User created successfully")
    else:
        print("User already exists")

def init_weather_agent(db: Session):
    existing_agent = db.query(Agent).filter(Agent.name == 'weather').first()
    
    if not existing_agent:
        weather_config = {
            "temperature": 0.7
        }
        
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
        
def init_default_agent(db: Session):
    existing_agent = db.query(Agent).filter(Agent.name == 'default').first()
    
    if not existing_agent:
        config = {}
        
        agent = Agent(
            name='default',
            keywords='domyślny, default',
            configuration=config
        )
        
        db.add(agent)
        db.commit()
        print("Default agent created successfully")
    else:
        print("Default agent already exists")

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
    
    # Delete existing scheduler entries for this user and agent
    existing_schedulers = db.query(Scheduler).filter(
        Scheduler.user_id == user.id,
        Scheduler.agent_id == weather_agent.id
    ).all()
    
    for scheduler in existing_schedulers:
        db.delete(scheduler)
    
    if existing_schedulers:
        print(f"Deleted {len(existing_schedulers)} existing scheduler entries")
    
    # Define scheduler times and configurations
    scheduler_configs = [
        {"time": time(7, 0), "prompt": "Agent pogoda. Prognoza pogody.", "message_type": "voice"},
        {"time": time(12, 0), "prompt": "Agent pogoda. Prognoza pogody.", "message_type": "voice"},
        {"time": time(19, 0), "prompt": "Agent pogoda. Prognoza pogody.", "message_type": "voice"}
    ]
    
    # Create schedulers in a loop
    for i, config in enumerate(scheduler_configs, 1):
        scheduler = Scheduler(
            user_id=user.id,
            agent_id=weather_agent.id,
            time=config["time"],
            prompt=config["prompt"],
            message_type=config["message_type"]
        )
        
        db.add(scheduler)
        print(f"Scheduler {i} created successfully for {scheduler.time.strftime('%H:%M')} with ID: {scheduler.id}")
    
    db.commit()
    print(f"Created {len(scheduler_configs)} schedulers successfully")