from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, UTC

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    event_id: int
    registration_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "confirmado"  # confirmado, cancelado, etc.