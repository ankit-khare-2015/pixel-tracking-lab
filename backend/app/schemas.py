from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=100)
    event_time: datetime
    page_url: str | None = None
    referrer: str | None = None
    session_id: str | None = Field(default=None, max_length=100)
    anonymous_user_id: str | None = Field(default=None, max_length=100)
    user_agent: str | None = None
    language: str | None = Field(default=None, max_length=20)
    screen_width: int | None = None
    screen_height: int | None = None
    utm_source: str | None = Field(default=None, max_length=255)
    utm_medium: str | None = Field(default=None, max_length=255)
    utm_campaign: str | None = Field(default=None, max_length=255)
    utm_term: str | None = Field(default=None, max_length=255)
    utm_content: str | None = Field(default=None, max_length=255)
    payload_json: dict[str, Any] | None = None


class TrackEventRequest(EventBase):
    event_id: str | None = None


class EventResponse(EventBase):
    id: int
    event_id: str
    ip_address: str | None
    source_type: str

    model_config = ConfigDict(from_attributes=True)
