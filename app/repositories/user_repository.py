from app.models.user import User
from typing import List, Optional
from sqlmodel import Session, select # Añadir importaciones de SQLModel

class UserRepository:
    def __init__(self, db: Session): # Modificar el constructor para aceptar una sesión de BD
        self._db: Session = db # Almacenar la sesión de BD
        # self._id_counter = 1 # Ya no es necesario, la BD manejará los IDs

    def create(self, user: User) -> User:
        # user.id = self._id_counter # La BD asignará el ID automáticamente
        # self._id_counter += 1
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self._db.exec(statement).first()

    def get_by_identificacion(self, identificacion: str) -> Optional[User]:
        # return next((u for u in self._db if u.identificacion == identificacion), None)
        statement = select(User).where(User.identificacion == identificacion)
        return self._db.exec(statement).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        # return next((u for u in self._db if u.id == user_id), None)
        statement = select(User).where(User.id == user_id)
        return self._db.exec(statement).first()

    def list(self) -> List[User]:
        # return self._db
        statement = select(User)
        return self._db.exec(statement).all()

    def update_user_password(self, user_id: int, new_hashed_password: str):
        user = self.get_by_id(user_id)
        if user:
            user.hashed_password = new_hashed_password
            self._db.add(user)
            self._db.commit()
            self._db.refresh(user)
            return user
        return None
