import datetime

from database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(String, default="created")
    phone = Column(String, nullable=True)
    pushname = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String, default="operator")  # admin, operator
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String
    )  # to match frontend which expects string or we can use integer
    url = Column(String)
    events = Column(String)  # comma separated
    secret = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class MessageLog(Base):
    __tablename__ = "message_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer)
    msg_id = Column(String, unique=True, index=True)
    from_me = Column(Boolean, default=False)
    from_str = Column(String)
    to_str = Column(String)
    body = Column(String)
    type = Column(String)
    timestamp = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)
    severity = Column(String)  # low, medium, high
    session_id = Column(String, nullable=True)
    api_key_id = Column(String, nullable=True)
    details = Column(String, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
