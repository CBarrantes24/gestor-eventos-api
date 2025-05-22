import pytest
from app.services.event_service import EventService
from app.schemas.event import EventCreate
from app.models.event import EventStatus
from app.models.attendance import Attendance
from datetime import datetime, timezone  # Usar timezone en lugar de UTC

class TestAttendanceService:
    def setup_method(self):
        """Configuración inicial para cada prueba"""
        self.service = EventService()
        # Crear un evento para las pruebas
        self.event_data = EventCreate(
            title="Evento de Prueba",
            description="Descripción del evento de prueba",
            date="2025-06-15",
            start_time="14:00",
            end_time="16:00",
            organizer="Organizador de Prueba",
            capacity=10
        )
        self.event = self.service.create_event(self.event_data)
        
        # Crear un usuario para las pruebas (simulado)
        # En un entorno real, usaríamos el servicio de usuario
        self.user_id = 1
        self.service.user_repo._db = [type('User', (), {'id': self.user_id, 'nombre': 'Usuario Prueba', 'email': 'test@example.com'})]
    
    def test_register_attendee(self):
        """Prueba el registro de un asistente a un evento"""
        # Registrar un asistente
        updated_event = self.service.register_attendee(self.event.id, self.user_id)
        
        # Verificar que el contador de asistentes se incrementó
        assert updated_event.attendees == 1
        
        # Verificar que se creó el registro de asistencia
        attendance = self.service.attendance_repo.get_by_user_and_event(self.user_id, self.event.id)
        assert attendance is not None
        assert attendance.status == "confirmado"
        
        # Intentar registrar el mismo usuario nuevamente debería fallar
        with pytest.raises(ValueError, match="El usuario ya está registrado en este evento"):
            self.service.register_attendee(self.event.id, self.user_id)
    
    def test_register_attendee_invalid_event(self):
        """Prueba el registro a un evento inexistente"""
        with pytest.raises(ValueError, match="Evento no encontrado"):
            self.service.register_attendee(999, self.user_id)
    
    def test_register_attendee_invalid_user(self):
        """Prueba el registro con un usuario inexistente"""
        with pytest.raises(ValueError, match="Usuario no encontrado"):
            self.service.register_attendee(self.event.id, 999)
    
    def test_register_attendee_full_capacity(self):
        """Prueba el registro cuando el evento está a capacidad máxima"""
        # Crear un evento con capacidad 1
        event_data = EventCreate(
            title="Evento Capacidad Limitada",
            description="Evento con capacidad para una persona",
            date="2025-06-16",
            start_time="10:00",
            end_time="12:00",
            organizer="Organizador",
            capacity=1
        )
        event = self.service.create_event(event_data)
        
        # Registrar un asistente
        self.service.register_attendee(event.id, self.user_id)
        
        # Crear otro usuario
        user_id2 = 2
        self.service.user_repo._db.append(type('User', (), {'id': user_id2, 'nombre': 'Usuario 2', 'email': 'test2@example.com'}))
        
        # Intentar registrar otro asistente debería fallar
        with pytest.raises(ValueError, match="El evento ha alcanzado su capacidad máxima"):
            self.service.register_attendee(event.id, user_id2)
    
    def test_register_attendee_non_scheduled_event(self):
        """Prueba el registro a un evento que no está programado"""
        # Cambiar el estado del evento a EN_CURSO
        self.service.update_event_status(self.event.id, EventStatus.EN_CURSO)
        
        # Crear otro usuario
        user_id2 = 2
        self.service.user_repo._db.append(type('User', (), {'id': user_id2, 'nombre': 'Usuario 2', 'email': 'test2@example.com'}))
        
        # Intentar registrar un asistente debería fallar
        with pytest.raises(ValueError, match="No se puede registrar asistencia a un evento con estado"):
            self.service.register_attendee(self.event.id, user_id2)
    
    def test_cancel_attendance(self):
        """Prueba la cancelación de asistencia a un evento"""
        # Registrar un asistente
        self.service.register_attendee(self.event.id, self.user_id)
        
        # Cancelar la asistencia
        updated_event = self.service.cancel_attendance(self.event.id, self.user_id)
        
        # Verificar que el contador de asistentes se decrementó
        assert updated_event.attendees == 0
        
        # Verificar que se actualizó el estado de asistencia
        attendance = self.service.attendance_repo.get_by_user_and_event(self.user_id, self.event.id)
        assert attendance is not None
        assert attendance.status == "cancelado"
        
        # Intentar cancelar nuevamente debería fallar
        with pytest.raises(ValueError, match="El usuario no está registrado en este evento"):
            self.service.cancel_attendance(self.event.id, self.user_id)
    
    def test_cancel_attendance_invalid_event(self):
        """Prueba la cancelación de asistencia a un evento inexistente"""
        with pytest.raises(ValueError, match="Evento no encontrado"):
            self.service.cancel_attendance(999, self.user_id)
    
    def test_cancel_attendance_not_registered(self):
        """Prueba la cancelación de asistencia cuando el usuario no está registrado"""
        with pytest.raises(ValueError, match="El usuario no está registrado en este evento"):
            self.service.cancel_attendance(self.event.id, self.user_id)
    
    def test_cancel_attendance_non_scheduled_event(self):
        """Prueba la cancelación de asistencia a un evento que no está programado"""
        # Registrar un asistente
        self.service.register_attendee(self.event.id, self.user_id)
        
        # Cambiar el estado del evento a EN_CURSO
        self.service.update_event_status(self.event.id, EventStatus.EN_CURSO)
        
        # Intentar cancelar la asistencia debería fallar
        with pytest.raises(ValueError, match="No se puede cancelar asistencia a un evento con estado"):
            self.service.cancel_attendance(self.event.id, self.user_id)
    
    def test_get_event_attendees(self):
        """Prueba la obtención de asistentes a un evento"""
        # Registrar varios asistentes
        self.service.register_attendee(self.event.id, self.user_id)
        
        # Crear otro usuario y registrarlo
        user_id2 = 2
        self.service.user_repo._db.append(type('User', (), {'id': user_id2, 'nombre': 'Usuario 2', 'email': 'test2@example.com'}))
        self.service.register_attendee(self.event.id, user_id2)
        
        # Obtener los asistentes
        attendees = self.service.get_event_attendees(self.event.id)
        
        # Verificar que se obtuvieron los asistentes correctos
        assert len(attendees) == 2
        assert attendees[0]["user_id"] == self.user_id
        assert attendees[1]["user_id"] == user_id2
    
    def test_get_event_attendees_invalid_event(self):
        """Prueba la obtención de asistentes a un evento inexistente"""
        with pytest.raises(ValueError, match="Evento no encontrado"):
            self.service.get_event_attendees(999)
    
    def test_get_user_events(self):
        """Prueba la obtención de eventos de un usuario"""
        # Registrar el usuario en varios eventos
        self.service.register_attendee(self.event.id, self.user_id)
        
        # Crear otro evento y registrar al usuario
        event_data2 = EventCreate(
            title="Otro Evento",
            description="Descripción de otro evento",
            date="2025-07-20",
            start_time="18:00",
            end_time="20:00",
            organizer="Otro Organizador",
            capacity=20
        )
        event2 = self.service.create_event(event_data2)
        self.service.register_attendee(event2.id, self.user_id)
        
        # Obtener los eventos del usuario
        events = self.service.get_user_events(self.user_id)
        
        # Verificar que se obtuvieron los eventos correctos
        assert len(events) == 2
        assert events[0]["event_id"] == self.event.id
        assert events[1]["event_id"] == event2.id
    
    def test_get_user_events_invalid_user(self):
        """Prueba la obtención de eventos de un usuario inexistente"""
        with pytest.raises(ValueError, match="Usuario no encontrado"):
            self.service.get_user_events(999)