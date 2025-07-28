from sqlalchemy import Column, String, UUID, BigInteger, ForeignKey, Integer, Float, JSON, Boolean, Time, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import text

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255))


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


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True,
                server_default=text('uuid_generate_v4()'))
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    agent_id = Column(PostgresUUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    value = Column(Text, nullable=False)
