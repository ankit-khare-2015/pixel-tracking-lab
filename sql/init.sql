CREATE TABLE IF NOT EXISTS tracking_events (
  id SERIAL PRIMARY KEY,
  event_id UUID NOT NULL UNIQUE,
  event_name VARCHAR(100) NOT NULL,
  event_time TIMESTAMPTZ NOT NULL,
  page_url TEXT,
  referrer TEXT,
  session_id VARCHAR(100),
  anonymous_user_id VARCHAR(100),
  user_agent TEXT,
  language VARCHAR(20),
  screen_width INTEGER,
  screen_height INTEGER,
  ip_address VARCHAR(64),
  utm_source VARCHAR(255),
  utm_medium VARCHAR(255),
  utm_campaign VARCHAR(255),
  utm_term VARCHAR(255),
  utm_content VARCHAR(255),
  payload_json JSONB,
  source_type VARCHAR(30) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracking_events_event_time ON tracking_events (event_time DESC);
CREATE INDEX IF NOT EXISTS idx_tracking_events_event_name ON tracking_events (event_name);
CREATE INDEX IF NOT EXISTS idx_tracking_events_session_id ON tracking_events (session_id);
CREATE INDEX IF NOT EXISTS idx_tracking_events_anonymous_user_id ON tracking_events (anonymous_user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_events_source_type ON tracking_events (source_type);
