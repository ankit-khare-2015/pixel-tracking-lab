# LinkedIn Newsletter — Pixel Tracking Lab

---

## Post Title
**I built a pixel tracking system from scratch — so you can finally see what's happening when websites "track" you**

---

## Post Body

Every website you visit is firing invisible signals at a server.

You click a button. A 1×1 transparent image loads. A POST request fires. A database row is written.

Most developers use Google Analytics or Segment and never think twice about the plumbing underneath. I did think twice — and then I built it myself.

---

**What I built: pixel-tracking-lab**

A fully local, Dockerized analytics pipeline that works exactly like real ad-tech infrastructure:

- A demo website with a simulated e-commerce funnel (Home → Product → Signup → Checkout)
- A JavaScript tracking library (`window.myPixel`) that auto-fires events on page load and captures clicks, UTM parameters, session IDs, and browser metadata
- A FastAPI backend with two tracking endpoints: `POST /track` (JSON beacon) and `GET /pixel` (the classic 1×1 GIF trick used in email opens and display ads)
- PostgreSQL to store every event with full context
- Metabase for dashboards — event counts, funnel analysis, UTM campaign attribution

The whole thing spins up with one command: `docker compose up --build`

---

**Why the image pixel trick?**

The `GET /pixel` endpoint returns a transparent 1×1 GIF. That's it.

But because it's an image request, it fires even in environments where JavaScript is blocked — like email clients. That's how email open tracking works. Every "we can see you opened this" in your inbox is a tiny invisible image request hitting a server.

Seeing it work in your own stack makes it click in a way no article ever did for me.

---

**What I learned building this:**

- How anonymous user identity works across sessions (localStorage + UUID)
- How UTM attribution flows from URL → event → database → dashboard
- Why JSON POST and image GET exist as two different tracking methods and when to use each
- How Metabase connects to raw Postgres to build funnel charts without a data warehouse
- How FastAPI handles CORS, health checks, and async DB writes in production-grade patterns

---

**This is not a tutorial. It's a lab.**

No step-by-step hand-holding. You clone it, run it, break it, inspect it. Open the database directly. Fire events from curl. Build a Metabase chart. Add a new event type.

That hands-on approach is the only way I actually learn something.

---

If you want to understand how analytics infrastructure works — not just use it — this project is for you.

GitHub link in the comments.

What part of modern tracking infrastructure do you find most interesting or surprising? Drop it below.

---

#DataEngineering #ProductAnalytics #Python #FastAPI #Docker #WebTracking #Analytics #OpenSource #LearningByBuilding #AdTech

---

## Video Script (Screen Recording — ~3-4 minutes)

**Intro (0:00–0:20)**
> "I'm going to show you how browser pixel tracking works — by running the entire system locally. This is pixel-tracking-lab: a FastAPI backend, a PostgreSQL database, a Metabase dashboard, and a demo website — all running in Docker."

**Start the Stack (0:20–0:45)**
```bash
cd pixel-tracking-lab
docker compose up --build -d
```
> "One command. Four containers. Let's wait for them to be healthy."

**Demo Site (0:45–1:20)**
- Open http://localhost:8080
> "Here's the demo site. Four pages simulating a product funnel. When this page loaded, a `page_view` event just fired automatically."
- Click "Add to Cart" on the product page
> "That button just called `window.myPixel.track('add_to_cart', ...)` which POSTed JSON to our backend."

**Live Events Feed (1:20–1:50)**
- Open http://localhost:8080/events.html
> "Here's the live events feed. We can see both the `page_view` and `add_to_cart` events — with the session ID, UTM parameters, user agent, everything."

**API Docs (1:50–2:20)**
- Open http://localhost:8000/docs
> "The FastAPI backend has Swagger docs auto-generated. Two tracking endpoints: POST /track for JSON beacons and GET /pixel for image pixel beacons."
- Demonstrate GET /pixel in the Swagger UI
> "This endpoint returns a transparent 1×1 GIF. That's the old-school way email open tracking works — the image request carries the event data."

**Database (2:20–2:50)**
```bash
docker compose exec postgres psql -U pixel -d pixel_lab \
  -c "SELECT event_name, source_type, event_time FROM tracking_events ORDER BY id DESC LIMIT 10;"
```
> "Here's the raw data in PostgreSQL. You can see js_pixel and image_pixel source types — same event, different transport."

**Metabase (2:50–3:30)**
- Open http://localhost:3000
> "Metabase connects directly to the same Postgres database. I can build an event count chart, a funnel by page, or a breakdown by UTM campaign — no data warehouse required."

**Wrap Up (3:30–4:00)**
> "That's the full loop: browser fires event → FastAPI validates and stores it → PostgreSQL persists it → Metabase visualizes it. The same architecture that powers real analytics systems — running locally in 4 Docker containers. Link in the description."
