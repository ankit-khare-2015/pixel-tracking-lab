import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import TrackEventRequest
from app.services.event_service import create_js_event

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/track")
def track_event(payload: TrackEventRequest, request: Request, db: Session = Depends(get_db)):
    try:
        event = create_js_event(db, request, payload)
        return {"status": "ok", "event_id": event.event_id}
    except SQLAlchemyError as exc:
        logger.exception("Database error while saving /track event: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to save event") from exc
    except Exception as exc:
        logger.exception("Unexpected error in /track: %s", exc)
        raise HTTPException(status_code=500, detail="Unexpected error") from exc
