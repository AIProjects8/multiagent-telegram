from sqlalchemy import create_engine
from sqlalchemy.orm import Session
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

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()