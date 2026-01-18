from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    duration_seconds: int
    look_away_count: int
    total_look_away_duration: float
    tab_switch_count: int
    task: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
