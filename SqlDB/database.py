from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from .models import Base
from SqlDB.SampleData.db_initializer import init_user, init_agent_item, init_weather_agent, init_default_agent, init_time_agent, init_time_agent_item, init_scheduler, init_configuration_agent
from config import Config

def get_database_url(): 
    config = Config.from_env()
    
    print(f"POSTGRES_USER: {config.postgres_user}")
    print(f"POSTGRES_PASSWORD: {config.postgres_password}")
    print(f"POSTGRES_DB: {config.postgres_db}")
    print(f"POSTGRES_HOST: {config.postgres_host}")
    print(f"POSTGRES_PORT: {config.postgres_port}")
    
    return f'postgresql://{config.postgres_user}:{config.postgres_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}'

engine = create_engine(get_database_url())

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = ['users', 'agents', 'agent_items', 'scheduler', 'conversation_history']
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
        
        Base.metadata.create_all(bind=engine)
        print(f"Database tables created successfully: {missing_tables}")
    else:
        print("All required database tables already exist")
    
    db = Session(engine)
    try:
        init_user(db)   
        init_weather_agent(db)
        init_default_agent(db)
        init_time_agent(db)
        init_agent_item(db)
        init_time_agent_item(db)
        init_scheduler(db)
        init_configuration_agent(db)
    finally:
        db.close()

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()