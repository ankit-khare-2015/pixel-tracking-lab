import logging
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Request
from sqlalchemy.orm import Session

from app import models
from app.schemas import TrackEventRequest

logger = logging.getLogger(__name__)


def _extract_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _safe_datetime(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def create_js_event(db: Session, request: Request, payload: TrackEventRequest) -> models.TrackingEvent:
    event = models.TrackingEvent(
        event_id=payload.event_id or str(uuid4()),
        event_name=payload.event_name,
        event_time=_safe_datetime(payload.event_time),
        page_url=payload.page_url,
        referrer=payload.referrer,
        session_id=payload.session_id,
        anonymous_user_id=payload.anonymous_user_id,
        user_agent=payload.user_agent,
        language=payload.language,
        screen_width=payload.screen_width,
        screen_height=payload.screen_height,
        ip_address=_extract_client_ip(request),
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
        utm_term=payload.utm_term,
        utm_content=payload.utm_content,
        payload_json=payload.payload_json,
        source_type="js_pixel",
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_image_pixel_event(
    db: Session,
    request: Request,
    *,
    event_name: str,
    page_url: str | None,
    session_id: str | None,
    anonymous_user_id: str | None,
    payload_json: dict | None,
) -> models.TrackingEvent:
    event = models.TrackingEvent(
        event_id=str(uuid4()),
        event_name=event_name,
        event_time=datetime.now(UTC),
        page_url=page_url,
        referrer=request.headers.get("referer"),
        session_id=session_id,
        anonymous_user_id=anonymous_user_id,
        user_agent=request.headers.get("user-agent"),
        language=request.headers.get("accept-language"),
        screen_width=None,
        screen_height=None,
        ip_address=_extract_client_ip(request),
        utm_source=payload_json.get("utm_source") if payload_json else None,
        utm_medium=payload_json.get("utm_medium") if payload_json else None,
        utm_campaign=payload_json.get("utm_campaign") if payload_json else None,
        utm_term=payload_json.get("utm_term") if payload_json else None,
        utm_content=payload_json.get("utm_content") if payload_json else None,
        payload_json=payload_json,
        source_type="image_pixel",
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event
