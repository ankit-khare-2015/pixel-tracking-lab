# Pixel Tracking Lab

> A hands-on, fully Dockerized lab to learn how **browser pixel tracking** and **product analytics pipelines** work end-to-end — the same way companies like Segment, Mixpanel, and Google Analytics work under the hood.

---

## What Is This Project?

Every time you visit a website and see "We track your activity to improve our service," there is an invisible tracking pixel or JavaScript beacon firing in the background. This project builds that entire system from scratch — so you can **see, understand, and extend it**.

This is not a tutorial you follow passively. You run a real 4-service stack, fire real events from real web pages, and watch them land in a real database — then visualize them in Metabase.

**Built for:** developers, data engineers, growth engineers, and anyone curious about how analytics infrastructure actually works.

---

## Architecture Overview

```
Browser (Demo Site)
  │
  ├── POST /track  ──► FastAPI Backend ──► PostgreSQL ──► Metabase
  │   (JSON beacon)
  └── GET /pixel   ──► FastAPI Backend ──► PostgreSQL
      (1×1 GIF beacon)
```

### The 4 Services (all via Docker Compose)

| Service       | URL                        | What It Does                             |
|---------------|----------------------------|------------------------------------------|
| Demo Site     | http://localhost:8080      | HTML pages that fire tracking events     |
| FastAPI API   | http://localhost:8000/docs | Receives, validates, stores events       |
| PostgreSQL    | port 5432                  | Stores all tracking data                 |
| Metabase      | http://localhost:3000      | Analytics & dashboard UI                 |

---

## Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| Backend     | Python 3.12, FastAPI, SQLAlchemy 2, Uvicorn |
| Database    | PostgreSQL 16                             |
| Frontend    | Vanilla HTML, CSS, JavaScript             |
| Analytics   | Metabase                                  |
| Infra       | Docker Compose                            |

---

## What Was Built

### Demo Site (`demo-site/`)
Five pages that simulate a real e-commerce funnel:
- `index.html` — Home page
- `product.html` — Product detail page
- `signup.html` — User registration page
- `checkout.html` — Checkout & purchase page
- `events.html` — Live feed of recent tracking events
- `reports.html` — Links to Metabase dashboards

### JavaScript Tracking Library (`demo-site/js/pixel.js`)
`window.myPixel` — a lightweight tracking client that:
- Fires `page_view` automatically on every page load
- Exposes `window.myPixel.track(eventName, payload)` for custom events
- Persists `anonymous_user_id` and `session_id` in `localStorage`
- Captures UTM parameters from the URL (source, medium, campaign, term, content)
- Enriches every event with browser metadata: user agent, language, screen size, referrer, timestamp
- Supports **two transport methods**: JSON POST and image pixel GET

### FastAPI Backend (`backend/`)
Four endpoints:
- `GET /health` — liveness check
- `POST /track` — receives JSON events from JS beacon
- `GET /pixel` — receives events via URL params, returns a transparent 1×1 GIF
- `GET /events?limit=100` — returns recent events for the live feed page

### PostgreSQL Schema (`sql/init.sql`)
One table — `tracking_events` — with:
- `event_id` (UUID, primary key)
- `event_name`, `event_time`, `page_url`, `referrer`
- `session_id`, `anonymous_user_id`
- `user_agent`, `screen_width`, `screen_height`
- `ip_address`
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
- `payload_json` (JSONB — free-form data per event)
- `source_type` (`js_pixel` or `image_pixel`)

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running on your machine
- That's it.

### Run

```bash
git clone <repo-url>
cd pixel-tracking-lab
cp .env.example .env
docker compose up --build
```

Wait ~30 seconds for all services to initialize, then open:

| What               | URL                               |
|--------------------|-----------------------------------|
| Demo Site          | http://localhost:8080             |
| Live Events Feed   | http://localhost:8080/events.html |
| API Swagger Docs   | http://localhost:8000/docs        |
| Metabase Dashboard | http://localhost:3000             |

### Stop

```bash
docker compose down
```

### Reset (wipe data)

```bash
docker compose down -v
```

---

## Testing the System

### Scenario 1 — Basic Event Flow

1. Open http://localhost:8080
2. Navigate: Home → Product → Signup → Checkout
3. Click the action buttons on each page
4. Open http://localhost:8080/events.html

**Expect:** `page_view` events auto-fired per page load, plus custom events per button click.

---

### Scenario 2 — UTM Campaign Attribution

Open the site with UTM parameters:

```
http://localhost:8080?utm_source=newsletter&utm_medium=email&utm_campaign=spring_launch
```

Fire a few events, then check:

```bash
curl "http://localhost:8000/events?limit=5"
```

**Expect:** Events carry `utm_source`, `utm_medium`, `utm_campaign` in the response.

---

### Scenario 3 — Image Pixel Tracking

Click the button that uses the image pixel transport on the Home page.

**Expect:** An event stored with `source_type = image_pixel` — the same data, different delivery mechanism.

---

### Scenario 4 — API & Database Inspection

```bash
# Health check
curl http://localhost:8000/health

# Recent events via API
curl "http://localhost:8000/events?limit=20"

# Direct database query
docker compose exec postgres psql -U pixel -d pixel_lab \
  -c "SELECT event_name, source_type, event_time FROM tracking_events ORDER BY id DESC LIMIT 20;"
```

---

### Scenario 5 — Metabase Dashboards

1. Open http://localhost:3000
2. Connect to PostgreSQL with:
   - Host: `postgres`
   - Port: `5432`
   - Database: `pixel_lab`
   - User: `pixel`
   - Password: `pixel`
3. Browse the `tracking_events` table
4. Build charts: event counts by name, funnel by page, events by UTM campaign

---

## How Pixel Tracking Works (Concept)

### JavaScript Beacon (Modern)
```javascript
window.myPixel.track("add_to_cart", { product_id: "SKU-42", price: 49.99 });
// → POST /track with JSON body
// → Stored as source_type = js_pixel
```

### Image Pixel Beacon (Classic / Ad-Tech)
```html
<img src="http://localhost:8000/pixel?event=add_to_cart&product_id=SKU-42" width="1" height="1" />
// → GET /pixel → returns transparent 1×1 GIF
// → Stored as source_type = image_pixel
```

The image pixel trick works even in environments where JavaScript is blocked — historically used in email open tracking and display advertising.

---

## Project Structure

```
pixel-tracking-lab/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          ← FastAPI app, CORS, startup
│       ├── config.py        ← Settings via pydantic-settings
│       ├── db.py            ← Engine, session, retry logic
│       ├── models.py        ← TrackingEvent ORM model
│       ├── schemas.py       ← Pydantic request/response schemas
│       ├── routes/
│       │   ├── health.py
│       │   ├── track.py     ← POST /track
│       │   ├── pixel.py     ← GET /pixel
│       │   └── events.py    ← GET /events
│       ├── services/
│       │   └── event_service.py
│       └── utils/
│           └── transparent_pixel.py
│
├── demo-site/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── product.html
│   ├── signup.html
│   ├── checkout.html
│   ├── events.html
│   ├── reports.html
│   ├── js/
│   │   ├── pixel.js         ← window.myPixel tracking library
│   │   └── app.js           ← Page-specific event bindings
│   └── css/
│       └── styles.css
│
└── sql/
    └── init.sql             ← Schema + indexes
```

---

## Done Criteria (All Achieved)

- [x] Docker Compose starts all 4 services cleanly
- [x] Demo pages fire automatic `page_view` events on load
- [x] Button clicks generate custom events via JS beacon
- [x] Image pixel endpoint returns valid 1×1 GIF and stores events
- [x] PostgreSQL contains tracking rows with full metadata
- [x] UTM parameters are captured and stored correctly
- [x] Metabase can connect and query tracking data
- [x] Live events feed page shows real-time data

---

## Author

Built to understand the internals of analytics infrastructure — no third-party SDKs, no magic, just the real thing.
