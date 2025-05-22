from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    identificacion: str
    nombre: str
    email: str
    rol: str  # 'Admin', 'Organizador', 'Asistente'
    
    

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    fecha_creacion: datetime

class UserLogin(SQLModel):
    email: str
    password: str

class TokenResponse(SQLModel):
    access_token: str
    token_type: str
    user: UserRead
