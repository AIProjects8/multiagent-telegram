from sqlalchemy import Column, String, UUID, BigInteger, ForeignKey, Integer, Float, JSON, Boolean, Time, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import text
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255))
    configuration = Column(JSON, nullable=True)


class Agent(Base):
    __tablename__ = 'agents'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    name = Column(String(255), nullable=False)
    keywords = Column(String(1000), nullable=False)
    configuration = Column(JSON)


class AgentItem(Base):
    __tablename__ = 'agent_items'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    agent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    questionnaire_answers = Column(JSON)
    questionnaire_completed = Column(Boolean, default=False, nullable=False)


class Scheduler(Base):
    __tablename__ = 'scheduler'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    agent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    time = Column(Time, nullable=False)
    prompt = Column(Text, nullable=False)
    message_type = Column(String(10), nullable=False, default='text')


class ConversationHistory(Base):
    __tablename__ = 'conversation_history'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    agent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_id = Column(String(255), nullable=False)
