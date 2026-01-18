from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="owner")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration_seconds = Column(Integer)
    look_away_count = Column(Integer)
    total_look_away_duration = Column(Float)
    tab_switch_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task = Column(String, nullable=True)

    owner = relationship("User", back_populates="sessions")
