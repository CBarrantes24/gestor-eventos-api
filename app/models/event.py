from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum, auto


class EventStatus(str, Enum):
    PROGRAMADO = "programado"
    EN_CURSO = "en_curso"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str
    date: str
    organizer: str
    capacity: int  # Capacidad máxima del evento
    attendees: int = 0  # Número actual de asistentes
    status: EventStatus = EventStatus.PROGRAMADO
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None