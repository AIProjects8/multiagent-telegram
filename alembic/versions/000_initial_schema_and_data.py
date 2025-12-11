"""initial schema and data

Revision ID: 000
Revises: 
Create Date: 2024-12-08 22:00:00.000000

"""
from typing import Sequence, Union
import json
from datetime import time

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False, unique=True),
        sa.Column('chat_id', sa.BigInteger(), nullable=False, unique=True),
        sa.Column('name', sa.String(255)),
        sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('keywords', sa.String(1000), nullable=False),
        sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('display_name', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    
    op.create_table(
        'agent_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('questionnaire_answers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('questionnaire_completed', sa.Boolean(), nullable=False, server_default='false')
    )
    
    op.create_table(
        'scheduler',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(10), nullable=False, server_default='text')
    )
    
    op.create_table(
        'conversation_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('session_id', sa.String(255), nullable=False)
    )
    
    existing_user = conn.execute(
        text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
        {"telegram_id": 8133073522}
    ).fetchone()
    
    if existing_user:
        user_id = existing_user[0]
    else:
        user_result = conn.execute(
            text("""
                INSERT INTO users (telegram_id, chat_id, name, configuration)
                VALUES (:telegram_id, :chat_id, :name, :configuration)
                RETURNING id
            """),
            {
                "telegram_id": 8133073522,
                "chat_id": 8133073522,
                "name": "Test User",
                "configuration": None
            }
        )
        user_id = user_result.fetchone()[0]
    
    agents_data = [
        {
            'name': 'configuration',
            'keywords': 'konfiguracja,konfig,config',
            'configuration': json.dumps({'temperature': 0.1}),
            'display_name': json.dumps({"en": "Configuration", "pl": "Konfiguracja"})
        },
        {
            'name': 'weather',
            'keywords': 'pogoda,pogodowy,pogodny,pogodę,pogode',
            'configuration': json.dumps({'temperature': 0.7}),
            'display_name': json.dumps({"en": "Weather", "pl": "Pogoda"})
        },
        {
            'name': 'default',
            'keywords': 'domyślny, default',
            'configuration': json.dumps({'temperature': 0.7}),
            'display_name': json.dumps({"en": "Default", "pl": "Domyślny"})
        },
        {
            'name': 'time',
            'keywords': 'czas,zegarek',
            'configuration': json.dumps({'temperature': 0.7}),
            'display_name': json.dumps({"en": "Time", "pl": "Czas"})
        },
        {
            'name': 'youtube',
            'keywords': 'youtube',
            'configuration': json.dumps({'temperature': 0.7}),
            'display_name': json.dumps({"en": "YouTube", "pl": "YouTube"})
        },
        {
            'name': 'calculator',
            'keywords': 'kalkulator',
            'configuration': json.dumps({'temperature': 0.2}),
            'display_name': json.dumps({"en": "Calculator", "pl": "Kalkulator"})
        }
    ]
    
    agent_ids = {}
    for agent_data in agents_data:
        existing_agent = conn.execute(
            text("SELECT id FROM agents WHERE name = :name"),
            {"name": agent_data['name']}
        ).fetchone()
        
        if existing_agent:
            agent_id = existing_agent[0]
        else:
            result = conn.execute(
                text("""
                    INSERT INTO agents (name, keywords, configuration, display_name)
                    VALUES (:name, :keywords, CAST(:configuration AS jsonb), CAST(:display_name AS jsonb))
                    RETURNING id
                """),
                agent_data
            )
            agent_id = result.fetchone()[0]
        agent_ids[agent_data['name']] = agent_id
    
    weather_agent_id = agent_ids['weather']
    time_agent_id = agent_ids['time']
    
    existing_weather_item = conn.execute(
        text("SELECT id FROM agent_items WHERE user_id = :user_id AND agent_id = :agent_id"),
        {"user_id": user_id, "agent_id": weather_agent_id}
    ).fetchone()
    
    if not existing_weather_item:
        conn.execute(
            text("""
                INSERT INTO agent_items (user_id, agent_id, questionnaire_answers, questionnaire_completed)
                VALUES (:user_id, :agent_id, CAST(:questionnaire_answers AS jsonb), :questionnaire_completed)
            """),
            {
                "user_id": user_id,
                "agent_id": weather_agent_id,
                "questionnaire_answers": json.dumps({
                    "city_name": "Katowice",
                    "city_lat": 50.2644,
                    "city_lon": 19.0232
                }),
                "questionnaire_completed": True
            }
        )
    
    existing_time_item = conn.execute(
        text("SELECT id FROM agent_items WHERE user_id = :user_id AND agent_id = :agent_id"),
        {"user_id": user_id, "agent_id": time_agent_id}
    ).fetchone()
    
    if not existing_time_item:
        conn.execute(
            text("""
                INSERT INTO agent_items (user_id, agent_id, questionnaire_answers, questionnaire_completed)
                VALUES (:user_id, :agent_id, CAST(:questionnaire_answers AS jsonb), :questionnaire_completed)
            """),
            {
                "user_id": user_id,
                "agent_id": time_agent_id,
                "questionnaire_answers": json.dumps({
                    "city_name": "Katowice",
                    "city_lat": 50.2644,
                    "city_lon": 19.0232
                }),
                "questionnaire_completed": True
            }
        )
    
    existing_scheduler = conn.execute(
        text("SELECT id FROM scheduler WHERE user_id = :user_id AND agent_id = :agent_id AND time = :time"),
        {"user_id": user_id, "agent_id": weather_agent_id, "time": time(7, 0)}
    ).fetchone()
    
    if not existing_scheduler:
        conn.execute(
            text("""
                INSERT INTO scheduler (user_id, agent_id, time, prompt, message_type)
                VALUES (:user_id, :agent_id, :time, :prompt, :message_type)
            """),
            {
                "user_id": user_id,
                "agent_id": weather_agent_id,
                "time": time(7, 0),
                "prompt": "Agent pogoda. Prognoza pogody.",
                "message_type": "voice"
            }
        )


def downgrade() -> None:
    op.drop_table('conversation_history')
    op.drop_table('scheduler')
    op.drop_table('agent_items')
    op.drop_table('agents')
    op.drop_table('users')
