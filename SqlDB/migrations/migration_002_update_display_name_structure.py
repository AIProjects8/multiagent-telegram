from sqlalchemy import text

def upgrade(conn):
    conn.execute(text("""
        DO $$ 
        DECLARE
            agent_record RECORD;
            old_display_name JSONB;
            new_display_name JSONB;
            item JSONB;
            lang TEXT;
            name_val TEXT;
        BEGIN
            FOR agent_record IN SELECT id, display_name FROM agents WHERE display_name IS NOT NULL
            LOOP
                old_display_name := agent_record.display_name;
                
                IF jsonb_typeof(old_display_name) = 'array' THEN
                    new_display_name := '{}'::jsonb;
                    
                    FOR item IN SELECT * FROM jsonb_array_elements(old_display_name)
                    LOOP
                        lang := item->>'language';
                        name_val := item->>'name';
                        
                        IF lang IS NOT NULL AND name_val IS NOT NULL THEN
                            new_display_name := new_display_name || jsonb_build_object(lang, name_val);
                        END IF;
                    END LOOP;
                    
                    UPDATE agents 
                    SET display_name = new_display_name 
                    WHERE id = agent_record.id;
                    
                    RAISE NOTICE 'Updated display_name for agent %', agent_record.id;
                END IF;
            END LOOP;
        END $$;
    """))

