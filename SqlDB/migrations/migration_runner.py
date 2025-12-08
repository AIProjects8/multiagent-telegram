from sqlalchemy import create_engine, inspect, text, Column, String, DateTime
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from datetime import datetime
import os
import importlib.util
from pathlib import Path
from config import Config

MigrationBase = declarative_base()

class MigrationRecord(MigrationBase):
    __tablename__ = 'migrations'
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String(255), unique=True, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def get_database_url():
    config = Config.from_env()
    return f'postgresql://{config.postgres_user}:{config.postgres_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}'

def ensure_migrations_table(engine):
    inspector = inspect(engine)
    if 'migrations' not in inspector.get_table_names():
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
        MigrationBase.metadata.create_all(bind=engine)
        print("Migrations table created")

def get_applied_migrations(engine):
    ensure_migrations_table(engine)
    db = Session(engine)
    try:
        records = db.query(MigrationRecord).all()
        return {record.name for record in records}
    finally:
        db.close()

def mark_migration_applied(engine, migration_name):
    ensure_migrations_table(engine)
    db = Session(engine)
    try:
        record = MigrationRecord(name=migration_name)
        db.add(record)
        db.commit()
        print(f"✓ Migration '{migration_name}' marked as applied")
    except Exception as e:
        db.rollback()
        print(f"Error marking migration as applied: {e}")
        raise
    finally:
        db.close()

def load_migration_file(migration_path):
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migrations():
    engine = create_engine(get_database_url())
    
    migrations_dir = Path(__file__).parent
    migration_files = sorted([f for f in os.listdir(migrations_dir) 
                             if f.startswith('migration_') and f.endswith('.py') 
                             and f != 'migration_runner.py'])
    
    if not migration_files:
        print("No migration files found")
        return
    
    applied_migrations = get_applied_migrations(engine)
    
    print(f"\n=== Running Database Migrations ===")
    print(f"Found {len(migration_files)} migration file(s)")
    print(f"Already applied: {len(applied_migrations)} migration(s)\n")
    
    for migration_file in migration_files:
        migration_name = migration_file.replace('.py', '')
        
        if migration_name in applied_migrations:
            print(f"⊘ Skipping '{migration_name}' (already applied)")
            continue
        
        migration_path = migrations_dir / migration_file
        print(f"→ Running '{migration_name}'...")
        
        try:
            module = load_migration_file(migration_path)
            
            if not hasattr(module, 'upgrade'):
                print(f"  ERROR: Migration '{migration_name}' missing 'upgrade' function")
                continue
            
            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    module.upgrade(conn)
                    trans.commit()
                    mark_migration_applied(engine, migration_name)
                    print(f"  ✓ Migration '{migration_name}' applied successfully")
                except Exception as e:
                    trans.rollback()
                    print(f"  ✗ Error applying migration '{migration_name}': {e}")
                    raise
        except Exception as e:
            print(f"  ✗ Failed to load/run migration '{migration_name}': {e}")
            raise
    
    print(f"\n=== Migrations completed ===\n")

if __name__ == "__main__":
    run_migrations()

