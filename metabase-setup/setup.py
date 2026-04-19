"""
One-shot Metabase configurator.
Runs once after Metabase is healthy, then exits.
Skips silently if Metabase is already configured.

What it does:
  1. Waits for Metabase API to be ready
  2. Calls POST /api/setup  →  admin user + PostgreSQL connection in one shot
  3. Creates 3 pre-built questions (cards)
  4. Creates a "Pixel Tracking Lab" dashboard and pins all 3 cards to it
"""

import os, sys, time, json
import urllib.request, urllib.error

MB   = os.getenv("MB_URL", "http://metabase:3000")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB",  "pixel_lab")
DB_USER = os.getenv("POSTGRES_USER", "pixel")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "pixel")

ADMIN_EMAIL    = os.getenv("MB_ADMIN_EMAIL",    "admin@pixellab.local")
ADMIN_PASSWORD = os.getenv("MB_ADMIN_PASSWORD", "PixelLab2024!")
ADMIN_FNAME    = os.getenv("MB_ADMIN_FNAME",    "Pixel")
ADMIN_LNAME    = os.getenv("MB_ADMIN_LNAME",    "Admin")
SITE_NAME      = "Pixel Tracking Lab"


# ── helpers ──────────────────────────────────────────────────────────────────

def api(method: str, path: str, body=None, token: str = None) -> dict:
    url  = f"{MB}/api{path}"
    data = json.dumps(body).encode() if body is not None else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("X-Metabase-Session", token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def wait_for_metabase(max_wait=300):
    print(f"Waiting for Metabase at {MB} ...", flush=True)
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            props = api("GET", "/session/properties")
            setup_token = props.get("setup-token")
            if setup_token is None:
                print("Metabase is already configured — nothing to do.")
                sys.exit(0)
            print("Metabase is up. Setup token found.")
            return setup_token
        except Exception:
            time.sleep(5)
    print("ERROR: Metabase did not become ready in time.", flush=True)
    sys.exit(1)


# ── setup ────────────────────────────────────────────────────────────────────

def run_setup(setup_token: str) -> str:
    print("Running first-time setup ...", flush=True)
    result = api("POST", "/setup", {
        "token": setup_token,
        "user": {
            "email":      ADMIN_EMAIL,
            "password":   ADMIN_PASSWORD,
            "first_name": ADMIN_FNAME,
            "last_name":  ADMIN_LNAME,
            "site_name":  SITE_NAME,
        },
        "database": None,
        "prefs": {
            "site_name":      SITE_NAME,
            "allow_tracking": False,
            "site_locale":    "en",
        },
    })
    session_id = result.get("id")
    print(f"Setup complete. Session: {session_id[:8]}...", flush=True)
    return session_id


def add_database(token: str) -> int:
    print("Adding PostgreSQL database ...", flush=True)
    result = api("POST", "/database", {
        "engine": "postgres",
        "name":   "Pixel Lab DB",
        "details": {
            "host":     DB_HOST,
            "port":     DB_PORT,
            "dbname":   DB_NAME,
            "user":     DB_USER,
            "password": DB_PASS,
        },
        "auto_run_queries": True,
        "schedules": {},
    }, token=token)
    db_id = result["id"]
    print(f"  Database added: id={db_id}", flush=True)
    return db_id


def login() -> str:
    result = api("POST", "/session", {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    return result["id"]


def get_database_id(token: str) -> int:
    dbs = api("GET", "/database", token=token)
    for db in dbs.get("data", dbs if isinstance(dbs, list) else []):
        if db.get("name") == "Pixel Lab DB":
            return db["id"]
    raise RuntimeError("Could not find 'Pixel Lab DB' in Metabase databases")


def get_table_id(token: str, db_id: int) -> int:
    api("POST", f"/database/{db_id}/sync_schema", token=token)
    # poll until tracking_events appears (sync is async)
    for attempt in range(20):
        time.sleep(5)
        try:
            meta = api("GET", f"/database/{db_id}/metadata", token=token)
            for t in meta.get("tables", []):
                if t.get("name") == "tracking_events":
                    print(f"  tracking_events found (attempt {attempt+1})", flush=True)
                    return t["id"]
        except Exception:
            pass
        print(f"  waiting for sync ... ({attempt+1})", flush=True)
    raise RuntimeError("tracking_events table not found after sync")


def get_field_id(token: str, table_id: int, field_name: str) -> int | None:
    fields = api("GET", f"/table/{table_id}/query_metadata", token=token)
    for f in fields.get("fields", []):
        if f["name"] == field_name:
            return f["id"]
    return None


# ── questions (cards) ─────────────────────────────────────────────────────────

def create_card(token: str, name: str, db_id: int, dataset_query: dict, display: str, viz_settings: dict) -> int:
    result = api("POST", "/card", {
        "name":           name,
        "dataset_query":  dataset_query,
        "display":        display,
        "description":    None,
        "visualization_settings": viz_settings,
        "collection_id":  None,
    }, token=token)
    print(f"  Created card: {name} (id={result['id']})", flush=True)
    return result["id"]


def build_questions(token: str, db_id: int, table_id: int) -> list[int]:
    event_name_id  = get_field_id(token, table_id, "event_name")
    event_time_id  = get_field_id(token, table_id, "event_time")
    source_type_id = get_field_id(token, table_id, "source_type")
    utm_source_id  = get_field_id(token, table_id, "utm_source")

    card_ids = []

    # 1) Events by name — horizontal bar
    card_ids.append(create_card(
        token,
        "Events by Name",
        db_id,
        {
            "database": db_id,
            "type": "query",
            "query": {
                "source-table": table_id,
                "aggregation":  [["count"]],
                "breakout":     [[("field", event_name_id, None)] if event_name_id else []],
                "order-by":     [[("aggregation", 0), "desc"]],
                "limit":        20,
            },
        },
        "bar",
        {
            "graph.dimensions": ["event_name"],
            "graph.metrics":    ["count"],
            "graph.x_axis.title_text": "Event Name",
            "graph.y_axis.title_text": "Count",
        },
    ))

    # 2) Events over time — line chart (daily)
    card_ids.append(create_card(
        token,
        "Events Over Time (Daily)",
        db_id,
        {
            "database": db_id,
            "type": "query",
            "query": {
                "source-table": table_id,
                "aggregation":  [["count"]],
                "breakout":     [["field", event_time_id, {"temporal-unit": "day"}]] if event_time_id else [],
                "order-by":     [["asc", ["field", event_time_id, {"temporal-unit": "day"}]]] if event_time_id else [],
            },
        },
        "line",
        {
            "graph.dimensions": ["event_time"],
            "graph.metrics":    ["count"],
        },
    ))

    # 3) JS pixel vs image pixel — pie
    card_ids.append(create_card(
        token,
        "JS Pixel vs Image Pixel",
        db_id,
        {
            "database": db_id,
            "type": "query",
            "query": {
                "source-table": table_id,
                "aggregation":  [["count"]],
                "breakout":     [["field", source_type_id, None]] if source_type_id else [],
            },
        },
        "pie",
        {
            "pie.dimension": "source_type",
            "pie.metric":    "count",
        },
    ))

    # 4) Events by UTM source — bar
    card_ids.append(create_card(
        token,
        "Events by UTM Source",
        db_id,
        {
            "database": db_id,
            "type": "query",
            "query": {
                "source-table": table_id,
                "aggregation":  [["count"]],
                "breakout":     [["field", utm_source_id, None]] if utm_source_id else [],
                "order-by":     [[("aggregation", 0), "desc"]],
            },
        },
        "bar",
        {
            "graph.dimensions": ["utm_source"],
            "graph.metrics":    ["count"],
        },
    ))

    return card_ids


# ── dashboard ─────────────────────────────────────────────────────────────────

def create_dashboard(token: str, card_ids: list[int]) -> int:
    dash = api("POST", "/dashboard", {
        "name":        "Pixel Tracking Lab",
        "description": "Auto-generated dashboard — event volume, funnel, and UTM attribution.",
        "collection_id": None,
    }, token=token)
    dash_id = dash["id"]
    print(f"  Created dashboard id={dash_id}", flush=True)

    # layout: 2 columns × 2 rows, each card 12 wide × 8 tall
    positions = [
        (0, 0, 12, 8),
        (12, 0, 12, 8),
        (0, 8, 12, 8),
        (12, 8, 12, 8),
    ]
    cards_payload = [
        {
            "id":      -(i + 1),   # negative id = new dashcard
            "card_id": card_id,
            "col":     col,
            "row":     row,
            "size_x":  size_x,
            "size_y":  size_y,
            "parameter_mappings":     [],
            "visualization_settings": {},
            "series": [],
        }
        for i, (card_id, (col, row, size_x, size_y)) in enumerate(zip(card_ids, positions))
    ]
    api("PUT", f"/dashboard/{dash_id}/cards", {"cards": cards_payload}, token=token)

    print(f"  Dashboard ready: {MB}/dashboard/{dash_id}", flush=True)
    return dash_id


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    setup_token = wait_for_metabase()
    session_id  = run_setup(setup_token)

    # re-login to get a fresh session after setup
    time.sleep(3)
    token = login()

    print("Getting database and table IDs ...", flush=True)
    db_id    = add_database(token)
    table_id = get_table_id(token, db_id)
    print(f"  db_id={db_id}  table_id={table_id}", flush=True)

    print("Creating pre-built questions ...", flush=True)
    card_ids = build_questions(token, db_id, table_id)

    print("Creating dashboard ...", flush=True)
    dash_id = create_dashboard(token, card_ids)

    print(f"\nMetabase is ready.", flush=True)
    print(f"  Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}", flush=True)
    print(f"  Dashboard: {MB}/dashboard/{dash_id}", flush=True)


if __name__ == "__main__":
    main()
