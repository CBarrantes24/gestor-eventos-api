from app.models.attendance import Attendance
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import and_

class AttendanceRepository:
    def __init__(self, db: Session):
        self._db: Session = db

    def create(self, attendance: Attendance) -> Attendance:
        self._db.add(attendance)
        self._db.commit()
        self._db.refresh(attendance)
        return attendance
    
    def get(self, attendance_id: int) -> Optional[Attendance]:
        statement = select(Attendance).where(Attendance.id == attendance_id)
        return self._db.exec(statement).first()
    
    def get_by_user_and_event(self, user_id: int, event_id: int) -> Optional[Attendance]:
        statement = select(Attendance).where(
            and_(Attendance.user_id == user_id, Attendance.event_id == event_id)
        )
        return self._db.exec(statement).first()
    
    def get_by_event(self, event_id: int) -> List[Attendance]:
        statement = select(Attendance).where(Attendance.event_id == event_id)
        return self._db.exec(statement).all()
    
    def get_by_user(self, user_id: int) -> List[Attendance]:
        statement = select(Attendance).where(Attendance.user_id == user_id)
        return self._db.exec(statement).all()
    
    def delete(self, attendance_id: int) -> bool:
        db_attendance = self.get(attendance_id)
        if db_attendance:
            self._db.delete(db_attendance)
            self._db.commit()
            return True
        return False
    
    def update_status(self, attendance_id: int, status: str) -> Optional[Attendance]:
        db_attendance = self.get(attendance_id)
        if db_attendance:
            db_attendance.status = status
            self._db.add(db_attendance)
            self._db.commit()
            self._db.refresh(db_attendance)
            return db_attendance
        return None