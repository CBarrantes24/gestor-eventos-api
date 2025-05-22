from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional
from app.core.db import get_db
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventRead, EventUpdate
from app.models.event import EventStatus

router = APIRouter(prefix="/events", tags=["events"])

def get_event_service(db: Session = Depends(get_db)):
    return EventService(db=db)

@router.post("/", response_model=EventRead)
def create_event(
    event_data: EventCreate,
    service: EventService = Depends(get_event_service)
):
    try:
        event = service.create_event(event_data)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[EventRead])
def list_events(service: EventService = Depends(get_event_service)):
    return service.list_events()

@router.get("/search/", response_model=List[EventRead])
def search_events_by_name(
    name: str,
    service: EventService = Depends(get_event_service)
):
    return service.search_events_by_name(name)

@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: int,
    service: EventService = Depends(get_event_service)
):
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event

@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    try:
        event = service.update_event(event_id, event_data)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service)
):
    try:
        result = service.delete_event(event_id)
        if not result:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{event_id}/register/{user_id}", response_model=EventRead)
def register_attendee(
    event_id: int,
    user_id: int,
    service: EventService = Depends(get_event_service)
):
    try:
        event = service.register_attendee(event_id, user_id)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{event_id}/cancel/{user_id}", response_model=EventRead)
def cancel_attendance(
    event_id: int,
    user_id: int,
    service: EventService = Depends(get_event_service)
):
    try:
        event = service.cancel_attendance(event_id, user_id)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{event_id}/attendees")
def get_event_attendees(
    event_id: int,
    service: EventService = Depends(get_event_service)
):
    try:
        attendees = service.get_event_attendees(event_id)
        return attendees
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/user/{user_id}/events")
def get_user_events(
    user_id: int,
    service: EventService = Depends(get_event_service)
):
    try:
        events = service.get_user_events(user_id)
        return events
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{event_id}/status")
def update_event_status(
    event_id: int,
    status: EventStatus,
    service: EventService = Depends(get_event_service)
):
    event = service.update_event_status(event_id, status)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event