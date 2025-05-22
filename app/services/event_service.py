from app.schemas.event import EventCreate, EventUpdate
from app.models.event import Event, EventStatus
from sqlmodel import Session # Asegúrate de importar Session
from app.repositories.event_repository import EventRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.models.attendance import Attendance
from app.repositories.user_repository import UserRepository
from typing import List, Optional, Dict
from datetime import datetime, timezone, date, time  # Usar timezone en lugar de UTC

class EventService:
    def __init__(self, db: Session):
        self.event_repo = EventRepository(db=db)
        self.user_repo = UserRepository(db=db)
        self.attendance_repo = AttendanceRepository(db=db)

    def create_event(self, data: EventCreate) -> Event:
        # Validación de negocio: la capacidad debe ser mayor que cero
        if data.capacity <= 0:
            raise ValueError("La capacidad del evento debe ser mayor que cero")
        
        # Validación de fecha: no se puede crear un evento con fecha anterior a la actual
        try:
            event_date = datetime.strptime(data.date, "%Y-%m-%d").date()
            current_date = datetime.now().date()
            
            if event_date < current_date:
                raise ValueError("No se puede crear un evento con fecha anterior a la actual")
            
            # Si la fecha es hoy, validar que la hora de inicio sea posterior a la hora actual
            if event_date == current_date:
                event_start_time = datetime.strptime(data.start_time, "%H:%M").time()
                current_time = datetime.now().time()
                
                if event_start_time < current_time:
                    raise ValueError("No se puede crear un evento con hora de inicio anterior a la hora actual")
        except ValueError as e:
            if str(e).startswith("No se puede crear"):
                raise
            raise ValueError("Formato de fecha u hora inválido. Use YYYY-MM-DD para fecha y HH:MM para hora")
        
        event = Event(
            title=data.title, 
            description=data.description, 
            date=data.date, 
            start_time=data.start_time, 
            end_time=data.end_time, 
            organizer=data.organizer, 
            capacity=data.capacity,
            attendees=0,
            status=data.status
        )
        return self.event_repo.create(event)

    def list_events(self) -> List[Event]:
        return self.event_repo.list()
    
    def search_events_by_name(self, name: str) -> List[Event]:
        return self.event_repo.search_by_name(name)

    def get_event(self, event_id: int) -> Optional[Event]:
        return self.event_repo.get(event_id)

    def update_event(self, event_id: int, data: EventUpdate) -> Optional[Event]:
        # Validación de negocio: si se actualiza la capacidad, debe ser mayor o igual al número actual de asistentes
        event = self.event_repo.get(event_id)
        if not event:
            return None
            
        if data.capacity is not None and data.capacity < event.attendees:
            raise ValueError("La nueva capacidad no puede ser menor que el número actual de asistentes")
        
        # Validación de fecha: si se actualiza la fecha, no puede ser anterior a la actual
        if data.date is not None:
            try:
                event_date = datetime.strptime(data.date, "%Y-%m-%d").date()
                current_date = datetime.now().date()
                
                if event_date < current_date:
                    raise ValueError("No se puede actualizar un evento con fecha anterior a la actual")
                
                # Si la fecha es hoy y se actualiza la hora de inicio, validar que sea posterior a la hora actual
                if event_date == current_date and data.start_time is not None:
                    event_start_time = datetime.strptime(data.start_time, "%H:%M").time()
                    current_time = datetime.now().time()
                    
                    if event_start_time < current_time:
                        raise ValueError("No se puede actualizar un evento con hora de inicio anterior a la hora actual")
            except ValueError as e:
                if str(e).startswith("No se puede actualizar"):
                    raise
                raise ValueError("Formato de fecha u hora inválido. Use YYYY-MM-DD para fecha y HH:MM para hora")
        
        event_data = Event(
            title=data.title,
            description=data.description,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            organizer=data.organizer,
            capacity=data.capacity,
            status=data.status
        )
        return self.event_repo.update(event_id, event_data)

    def delete_event(self, event_id: int) -> bool:
        # Validación de negocio: no se puede eliminar un evento en curso
        event = self.event_repo.get(event_id)
        if event and event.status == EventStatus.EN_CURSO:
            raise ValueError("No se puede eliminar un evento que está en curso")
        
        return self.event_repo.delete(event_id)
    
    def register_attendee(self, event_id: int, user_id: int) -> Optional[Event]:
        # Verificar si el usuario ya está registrado en este evento
        existing_attendance = self.attendance_repo.get_by_user_and_event(user_id, event_id)
        if existing_attendance and existing_attendance.status == "confirmado":
            raise ValueError("El usuario ya está registrado en este evento")
        
        # Verificar si el usuario existe
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar si el evento existe y tiene capacidad
        event = self.event_repo.get(event_id)
        if not event:
            raise ValueError("Evento no encontrado")
        elif event.attendees >= event.capacity:
            raise ValueError("El evento ha alcanzado su capacidad máxima")
        elif event.status != EventStatus.PROGRAMADO:
            raise ValueError(f"No se puede registrar asistencia a un evento con estado {event.status}")
        
        # Validación de fecha y hora: no se puede registrar a un evento si la hora de inicio ya pasó
        try:
            event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
            event_start_time = datetime.strptime(event.start_time, "%H:%M").time()
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            
            if event_date < current_date or (event_date == current_date and event_start_time < current_time):
                raise ValueError("No se puede registrar a un evento que ya ha comenzado")
        except ValueError as e:
            if str(e).startswith("No se puede registrar"):
                raise
            raise ValueError("Error al procesar la fecha u hora del evento")
        
        # Si el usuario ya estaba registrado pero canceló, actualizamos su estado
        if existing_attendance:
            existing_attendance.status = "confirmado"
            self.attendance_repo.update_status(existing_attendance.id, "confirmado")
        else:
            # Crear nuevo registro de asistencia
            attendance = Attendance(
                user_id=user_id,
                event_id=event_id,
                status="confirmado"
            )
            # La fecha de registro se establecerá automáticamente por el valor predeterminado del modelo
            self.attendance_repo.create(attendance)
        
        # Actualizar contador de asistentes
        result = self.event_repo.register_attendee(event_id)
        return result
    
    def cancel_attendance(self, event_id: int, user_id: int) -> Optional[Event]:
        # Verificar si el evento existe
        event = self.event_repo.get(event_id)
        if not event:
            raise ValueError("Evento no encontrado")
        
        # Verificar si el usuario está registrado en este evento
        attendance = self.attendance_repo.get_by_user_and_event(user_id, event_id)
        if not attendance or attendance.status != "confirmado":
            raise ValueError("El usuario no está registrado en este evento")
        
        elif event.attendees <= 0:
            raise ValueError("No hay asistentes registrados para cancelar")
        elif event.status != EventStatus.PROGRAMADO:
            raise ValueError(f"No se puede cancelar asistencia a un evento con estado {event.status}")
        
        # Validación de fecha y hora: no se puede cancelar asistencia a un evento si la hora de inicio ya pasó
        try:
            event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
            event_start_time = datetime.strptime(event.start_time, "%H:%M").time()
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            
            if event_date < current_date or (event_date == current_date and event_start_time < current_time):
                raise ValueError("No se puede cancelar asistencia a un evento que ya ha comenzado")
        except ValueError as e:
            if str(e).startswith("No se puede cancelar"):
                raise
            raise ValueError("Error al procesar la fecha u hora del evento")
        
        # Actualizar estado de asistencia
        attendance.status = "cancelado"
        self.attendance_repo.update_status(attendance.id, "cancelado")
        
        # Actualizar contador de asistentes
        result = self.event_repo.cancel_attendance(event_id)
        return result
    
    def get_event_attendees(self, event_id: int) -> List[Dict]:
        # Verificar si el evento existe
        event = self.event_repo.get(event_id)
        if not event:
            raise ValueError("Evento no encontrado")
        
        # Obtener todas las asistencias confirmadas para este evento
        attendances = self.attendance_repo.get_by_event(event_id)
        confirmed_attendances = [a for a in attendances if a.status == "confirmado"]
        
        # Obtener información de los usuarios
        attendees = []
        for attendance in confirmed_attendances:
            user = self.user_repo.get_by_id(attendance.user_id)
            if user:
                attendees.append({
                    "user_id": user.id,
                    "nombre": user.nombre,
                    "email": user.email,
                    "registration_date": attendance.registration_date
                })
        
        return attendees
    
    def get_user_events(self, user_id: int) -> List[Dict]:
        # Verificar si el usuario existe
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Obtener todas las asistencias confirmadas para este usuario
        # Aquí está el problema - necesitamos usar select() en lugar de pasar la clase directamente
        attendances = self.attendance_repo.get_by_user(user_id)
        confirmed_attendances = [a for a in attendances if a.status == "confirmado"]
        
        # Obtener información de los eventos
        events = []
        for attendance in confirmed_attendances:
            event = self.event_repo.get(attendance.event_id)
            if event:
                events.append({
                    "event_id": event.id,
                    "title": event.title,
                    "date": event.date,
                    "status": event.status,
                    "registration_date": attendance.registration_date
                })
        
        return events
    
    def update_event_status(self, event_id: int, status: EventStatus) -> Optional[Event]:
        return self.event_repo.update_status(event_id, status)