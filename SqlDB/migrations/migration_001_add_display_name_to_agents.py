from sqlalchemy import text

def upgrade(conn):
    conn.execute(text("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'agents' 
                AND column_name = 'display_name'
            ) THEN
                ALTER TABLE agents ADD COLUMN display_name JSON;
                RAISE NOTICE 'Column display_name added to agents table';
            ELSE
                RAISE NOTICE 'Column display_name already exists in agents table';
            END IF;
        END $$;
    """))

