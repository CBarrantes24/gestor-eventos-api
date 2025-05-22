from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventUpdate
from app.models.event import EventStatus
import pytest

def test_create_event():
    service = EventService()
    data = EventCreate(
        title="Test Event",
        description="A test event",
        date="2025-05-20",
        start_time="10:00",
        end_time="12:00",
        organizer="Test User",
        capacity=100
    )
    event = service.create_event(data)
    assert event.id is not None
    assert event.title == "Test Event"
    assert event.organizer == "Test User"
    assert event.capacity == 100
    assert event.attendees == 0
    assert event.status == EventStatus.PROGRAMADO
    
def test_list_events():
    service = EventService()
    service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    service.create_event(EventCreate(title="B", description="desc", date="2025-05-21", start_time="11:00", end_time="13:00", organizer="Org2", capacity=20))
    events = service.list_events()
    assert len(events) == 2
    
def test_search_events_by_name():
    service = EventService()
    service.create_event(EventCreate(title="Evento de Programación", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    service.create_event(EventCreate(title="Evento de Diseño", description="desc", date="2025-05-21", start_time="11:00", end_time="13:00", organizer="Org2", capacity=20))
    
    events = service.search_events_by_name("Programación")
    assert len(events) == 1
    assert events[0].title == "Evento de Programación"
    
def test_get_event():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    assert event.id is not None
    found = service.get_event(event.id)
    assert found is not None
    assert found.title == "A"
    assert service.get_event(999) is None
    
def test_update_event():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    assert event.id is not None
    
    updated = service.update_event(event.id, EventUpdate(title="B", description="new", date="2025-05-21"))
    assert updated is not None
    assert updated.title == "B"
    assert updated.description == "new"
    
def test_delete_event():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    assert event.id is not None
    
    assert service.delete_event(event.id) is True
    assert service.get_event(event.id) is None
    assert service.delete_event(999) is False
    
def test_register_attendee():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    
    # Crear un usuario simulado
    user_id = 1
    service.user_repo._db = [type('User', (), {'id': user_id, 'nombre': 'Usuario Prueba', 'email': 'test@example.com'})]
    
    updated = service.register_attendee(event.id, user_id)
    assert updated.attendees == 1

def test_cancel_attendance():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    
    # Crear un usuario simulado
    user_id = 1
    service.user_repo._db = [type('User', (), {'id': user_id, 'nombre': 'Usuario Prueba', 'email': 'test@example.com'})]
    
    # Registrar un asistente primero
    service.register_attendee(event.id, user_id)
    
    # Ahora cancelar la asistencia
    updated = service.cancel_attendance(event.id, user_id)
    assert updated.attendees == 0
    
def test_update_event_status():
    service = EventService()
    event = service.create_event(EventCreate(title="A", description="desc", date="2025-05-20", start_time="10:00", end_time="12:00", organizer="Org", capacity=10))
    
    # Crear un usuario simulado para la prueba
    user_id = 1
    service.user_repo._db = [type('User', (), {'id': user_id, 'nombre': 'Usuario Prueba', 'email': 'test@example.com'})]
    
    # Cambiar estado a EN_CURSO
    updated = service.update_event_status(event.id, EventStatus.EN_CURSO)
    assert updated.status == EventStatus.EN_CURSO
    
    # No se puede registrar asistentes a un evento en curso
    with pytest.raises(ValueError) as excinfo:
        service.register_attendee(event.id, user_id)
    assert "No se puede registrar asistencia a un evento con estado" in str(excinfo.value)
    
    # No se puede eliminar un evento en curso
    with pytest.raises(ValueError, match="No se puede eliminar un evento que está en curso"):
        service.delete_event(event.id)
        
    # Cambiar estado a FINALIZADO (en lugar de COMPLETADO)
    updated = service.update_event_status(event.id, EventStatus.FINALIZADO)
    assert updated.status == EventStatus.FINALIZADO
    
    # Cambiar estado a CANCELADO
    updated = service.update_event_status(event.id, EventStatus.CANCELADO)
    assert updated.status == EventStatus.CANCELADO