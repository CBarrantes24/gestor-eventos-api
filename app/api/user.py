from fastapi import APIRouter, HTTPException, Depends # Añadir Depends
from app.schemas.user import UserCreate, UserRead, UserLogin, TokenResponse
from app.services.user_service import UserService
from typing import List
from app.core.db import get_db # Importar get_db
from sqlmodel import Session # Importar Session

router = APIRouter(prefix="/users", tags=["users"])
# Eliminar la instancia global: service = UserService()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)): # Inyectar db y crear service
    service = UserService(db=db) 
    try:
        return service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)): # Inyectar db y crear service
    service = UserService(db=db)
    result = service.authenticate_user(data.email, data.password)
    print(data)
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return result

@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)): # Inyectar db y crear service
    service = UserService(db=db)
    return service.list_users()
