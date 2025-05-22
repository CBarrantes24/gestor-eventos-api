from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identificacion: str
    nombre: str
    email: str
    hashed_password: str
    rol: str  # 'Admin', 'Organizador', 'Asistente'
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)