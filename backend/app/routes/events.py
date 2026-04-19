from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import TrackingEvent
from app.schemas import EventResponse

router = APIRouter()


@router.get("/events", response_model=list[EventResponse])
def list_events(limit: int = Query(default=100, ge=1, le=1000), db: Session = Depends(get_db)):
    events = (
        db.query(TrackingEvent)
        .order_by(desc(TrackingEvent.event_time))
        .limit(limit)
        .all()
    )
    return events
