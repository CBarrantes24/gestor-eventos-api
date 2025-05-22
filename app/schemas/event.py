from sqlmodel import SQLModel
from typing import Optional, List, Dict
from datetime import datetime
from app.models.event import EventStatus

class EventBase(SQLModel):
    title: str
    description: str
    date: str
    start_time: str
    end_time: str
    organizer: str
    capacity: int
    status: EventStatus = EventStatus.PROGRAMADO

class EventCreate(EventBase):
    pass

class EventUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    organizer: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[EventStatus] = None

class EventRead(EventBase):
    id: int
    attendees: int
    attendees_list: Optional[List[Dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None