from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from .models import Base

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
    
    # TODO: It's very primitive way to check if the database is initialized.
    # If you modified something into the database then remove docker container
    # with command: `docker compose down -v`
    if not existing_tables:
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    else:
        print("Database tables already exist")

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close() 