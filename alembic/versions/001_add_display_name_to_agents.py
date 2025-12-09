"""add display_name to agents

Revision ID: 001
Revises: 
Create Date: 2024-12-08 22:00:00.000000

"""
from typing import Sequence, Union
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text, table, column

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STANDARD_AGENTS_DISPLAY_NAMES = {
    'time': {"en": "Time", "pl": "Czas"},
    'weather': {"en": "Weather", "pl": "Pogoda"},
    'youtube': {"en": "YouTube", "pl": "YouTube"},
    'default': {"en": "Default", "pl": "Domyślny"},
    'configuration': {"en": "Configuration", "pl": "Konfiguracja"},
    'calculator': {"en": "Calculator", "pl": "Kalkulator"}
}

def upgrade() -> None:
    op.add_column('agents', sa.Column('display_name', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    conn = op.get_bind()
    agents_table = table('agents', column('id'), column('name'), column('display_name'))
    
    for agent in conn.execute(text("SELECT id, name FROM agents WHERE display_name IS NULL")):
        agent_id = agent[0]
        agent_name = agent[1]
        
        if agent_name in STANDARD_AGENTS_DISPLAY_NAMES:
            display_name = STANDARD_AGENTS_DISPLAY_NAMES[agent_name]
        else:
            capitalized_name = agent_name.capitalize()
            display_name = {
                "en": capitalized_name,
                "pl": capitalized_name
            }
        
        display_name_json = json.dumps(display_name)
        conn.execute(
            text("UPDATE agents SET display_name = CAST(:display_name_json AS jsonb) WHERE id = :agent_id"),
            {"display_name_json": display_name_json, "agent_id": agent_id}
        )


def downgrade() -> None:
    op.drop_column('agents', 'display_name')

