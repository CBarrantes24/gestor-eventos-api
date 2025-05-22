from app.models.event import Event, EventStatus
from typing import List, Optional
from datetime import datetime, time
# from sqlalchemy import or_ # Puedes necesitarlo para búsquedas complejas
from sqlmodel import Session, select, func # Añadir importaciones de SQLModel

class EventRepository:
    def __init__(self, db: Session): # Modificar el constructor
        self._db: Session = db # Almacenar la sesión de BD
        # self._id_counter = 1 # Ya no es necesario

    def create(self, event: Event) -> Event:
        # event.id = self._id_counter # La BD asignará el ID
        # self._id_counter += 1
        # event.created_at = datetime.now() # El modelo ya tiene default_factory
        self._db.add(event)
        self._db.commit()
        self._db.refresh(event)
        return event

    def list(self) -> List[Event]:
        # return self._db
        statement = select(Event)
        return self._db.exec(statement).all()
    
    def search_by_name(self, name: str) -> List[Event]:
        # En una implementación real con SQL, usaríamos LIKE o ILIKE
        # return [e for e in self._db if name.lower() in e.title.lower()]
        statement = select(Event).where(func.lower(Event.title).contains(name.lower()))
        return self._db.exec(statement).all()

    def get(self, event_id: int) -> Optional[Event]:
        # return next((e for e in self._db if e.id == event_id), None)
        statement = select(Event).where(Event.id == event_id)
        return self._db.exec(statement).first()

    def update(self, event_id: int, data: Event) -> Optional[Event]: # data debería ser un schema de actualización
        db_event = self.get(event_id)
        if db_event:
            update_data = data.model_dump(exclude_unset=True) # Usar model_dump para Pydantic/SQLModel
            for key, value in update_data.items():
                setattr(db_event, key, value)
            
            db_event.updated_at = datetime.now() # Asegúrate que UTC si es necesario
            self._db.add(db_event)
            self._db.commit()
            self._db.refresh(db_event)
            return db_event
        return None

    def delete(self, event_id: int) -> bool:
        db_event = self.get(event_id)
        if db_event:
            # self._db.remove(event)
            self._db.delete(db_event)
            self._db.commit()
            return True
        return False
    
    def register_attendee(self, event_id: int) -> Optional[Event]:
        db_event = self.get(event_id)
        if db_event and db_event.attendees < db_event.capacity and db_event.status == EventStatus.PROGRAMADO:
            db_event.attendees += 1
            db_event.updated_at = datetime.now() # Asegúrate que UTC si es necesario
            self._db.add(db_event)
            self._db.commit()
            self._db.refresh(db_event)
            return db_event
        return None
    
    def cancel_attendance(self, event_id: int) -> Optional[Event]:
        db_event = self.get(event_id)
        if db_event and db_event.attendees > 0 and db_event.status == EventStatus.PROGRAMADO:
            db_event.attendees -= 1
            db_event.updated_at = datetime.now() # Asegúrate que UTC si es necesario
            self._db.add(db_event)
            self._db.commit()
            self._db.refresh(db_event)
            return db_event
        return None
    
    def update_status(self, event_id: int, status: EventStatus) -> Optional[Event]:
        db_event = self.get(event_id)
        if db_event:
            db_event.status = status
            db_event.updated_at = datetime.now() # Asegúrate que UTC si es necesario
            self._db.add(db_event)
            self._db.commit()
            self._db.refresh(db_event)
            return db_event
        return None