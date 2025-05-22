from app.schemas.user import UserCreate, UserRead, UserLogin, TokenResponse
from app.models.user import User
from app.repositories.user_repository import UserRepository
from passlib.context import CryptContext # O importa pwd_context desde app.core.security
from typing import Optional
from datetime import datetime, UTC, timedelta
from jose import jwt
from sqlmodel import Session # Asegúrate de importar Session

# Import from config instead of main
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import get_password_hash, verify_password, pwd_context # Importa las utilidades y pwd_context
# from app.core.security import create_access_token # Si mueves la creación de token aquí
# from app.schemas.user import TokenResponse # Si mueves la creación de token aquí

class UserService:
    def __init__(self, db: Session): # Añadir db: Session como parámetro
        self.repo = UserRepository(db=db) # Pasar la sesión db al repositorio

    def list_users(self) -> list[UserRead]:
        users = self.repo.list()
        return [UserRead(
            id=u.id,
            identificacion=u.identificacion,
            nombre=u.nombre,
            email=u.email,
            rol=u.rol,
            fecha_creacion=u.fecha_creacion
        ) for u in users]

    def create_user(self, data: UserCreate) -> UserRead:
        # Convertir el email a minúsculas antes de cualquier validación o guardado
        email_lower = data.email.lower()
        # Validar unicidad de email e identificacion
        if self.repo.get_by_email(email_lower):
            raise ValueError("El correo ya está registrado")
        if self.repo.get_by_identificacion(data.identificacion):
            raise ValueError("La identificación ya está registrada")
        hashed_password = pwd_context.hash(data.password) # Ahora usará Argon2 por defecto
        user = User(
            identificacion=data.identificacion,
            nombre=data.nombre,
            email=email_lower,  # Guardar en minúsculas
            hashed_password=hashed_password,
            rol=data.rol,
            fecha_creacion=datetime.now(UTC)
        )
        user = self.repo.create(user)
        return UserRead(
            id=user.id or 0,
            identificacion=user.identificacion,
            nombre=user.nombre,
            email=user.email,
            rol=user.rol,
            fecha_creacion=user.fecha_creacion
        )

    def authenticate_user(self, email: str, password: str) -> Optional[TokenResponse]:
        # Convertir el email a minúsculas antes de buscar en la base de datos
        email_lower = email.lower()
        user = self.repo.get_by_email(email_lower)
        print(user)
        if user and pwd_context.verify(password, user.hashed_password):
            # Opcional: Lógica de re-hash si el hash actual es bcrypt
            if pwd_context.identify(user.hashed_password) == "bcrypt":
                # El usuario se autenticó con un hash bcrypt antiguo
                # Re-hashear con Argon2 y actualizar en la BD
                new_hashed_password = pwd_context.hash(password)
                user.hashed_password = new_hashed_password
                self.repo.update_user_password(user.id, new_hashed_password) # Necesitarías un método en el repo para esto

            user_data = UserRead(
                id=user.id,
                identificacion=user.identificacion,
                nombre=user.nombre,
                email=user.email,
                rol=user.rol,
                fecha_creacion=user.fecha_creacion
            )
            
            # Crear token JWT
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "rol": user.rol,
                "exp": datetime.now(UTC) + timedelta(hours=24)  # Token válido por 24 horas
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            return TokenResponse(
                access_token=token,
                token_type="bearer",
                user=user_data
            )
        return None


