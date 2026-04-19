import logging

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.event_service import create_image_pixel_event
from app.utils.transparent_pixel import TRANSPARENT_GIF_BYTES

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/pixel")
def pixel_track(
    request: Request,
    event: str = Query(default="page_view", max_length=100),
    page: str | None = Query(default=None),
    session_id: str | None = Query(default=None, max_length=100),
    uid: str | None = Query(default=None, max_length=100),
    utm_source: str | None = Query(default=None),
    utm_medium: str | None = Query(default=None),
    utm_campaign: str | None = Query(default=None),
    utm_term: str | None = Query(default=None),
    utm_content: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        payload = {
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
            "utm_term": utm_term,
            "utm_content": utm_content,
        }
        create_image_pixel_event(
            db,
            request,
            event_name=event,
            page_url=page,
            session_id=session_id,
            anonymous_user_id=uid,
            payload_json=payload,
        )
    except SQLAlchemyError as exc:
        logger.exception("Database error while saving /pixel event: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error in /pixel endpoint: %s", exc)

    return Response(content=TRANSPARENT_GIF_BYTES, media_type="image/gif")
