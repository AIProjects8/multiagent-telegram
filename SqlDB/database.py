from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from .models import Base
from SqlDB.SampleData.db_initializer import init_user, init_agent_item, init_weather_agent, init_default_agent, init_scheduler

load_dotenv()

def get_database_url(): 
    POSTGRES_USER = os.getenv('POSTGRES_USER') 
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') 
    POSTGRES_DB = os.getenv('POSTGRES_DB') 
    
    if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]): 
        raise EnvironmentError("Database environment variables are not fully set.") 
    return f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}'

engine = create_engine(get_database_url())

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = ['users', 'agents', 'agent_items', 'scheduler', 'conversations']
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
        init_agent_item(db)
        init_scheduler(db)
    finally:
        db.close()

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close() 