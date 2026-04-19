from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(UUID(as_uuid=False), unique=True, nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    page_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    anonymous_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    screen_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    screen_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
