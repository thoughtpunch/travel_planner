# Italy 2026 trip wiki

The live application is the Barrett family’s operational trip reference for
September 11–October 15, 2026. It keeps the itinerary, transport legs, stays,
activity choices and cost ledger in a real SQLite database.

The trip shape is booked. The app is for looking up facts and managing the
remaining variable pieces:

- choose, schedule and cost activities;
- see scheduled activities appear automatically on the dated itinerary;
- update booked, paid, cancelled and refunded costs in a shared ledger;
- keep travel legs, confirmations, stays and traveler constraints in separate
  durable tables.

## Run locally

Prerequisites: Python 3.12, `uv`, Node 22 and npm.

```bash
uv sync --extra dev
uv run alembic upgrade head
cd italy-trip-2026 && npm ci && npm run build && cd ..
uv run trip-planner serve
```

Open <http://127.0.0.1:8000>. On first start, the app imports the legacy Italy
itinerary and CSV ledgers into empty wiki tables. Later starts only add missing
source rows; edits made in the app are not overwritten.

For frontend work, run the API on port 8000 and `npm run dev` inside
`italy-trip-2026/`; Vite serves the wiki on port 5181 and proxies `/api`.

## Data model

Alembic owns the schema. The operational tables are:

| Table | Purpose |
|---|---|
| `wiki_traveler` | Party members, birthdays and constraints |
| `wiki_stop` | The eight bases and their dates |
| `wiki_leg` | Dated flights, trains, boats and car transfers |
| `wiki_stay` | Check-in/out facts, addresses and confirmations |
| `wiki_day` | One row per itinerary date |
| `wiki_itinerary_item` | Fixed events on a day |
| `activity_option` | Complete researched activity record: description, audience, image, maps, logistics, source detail, selection and schedule |
| `activity_attachment` | Ticket and confirmation files stored on the mounted volume |
| `trip_cost` | Shared booked/estimated/payment ledger |
| `wiki_setting` | Small trip-wide settings such as the budget |

`activity_option.scheduled_date` is the link into the itinerary. An activity
with status `selected`, `booked` or `done` and a date is rendered on that day.
The date picker and API restrict that date to the activity's `wiki_stop`
arrival-through-departure range.
Every active choice also owns one `trip_cost` row through
`trip_cost.activity_id`. Changes made on either Activities or Costs are applied
to both records in one database transaction. Cancelling removes an activity
from the active itinerary while retaining its paid, refunded and net amounts;
archiving either side archives both without destroying the history.
Activities marked `Won't do` remain in SQLite but are excluded from the normal
catalogue. The dedicated Status filter reveals them so they can be restored.

## Fly.io

The app is configured as `barrett-italy-2026` in `fly.toml`. SQLite lives on a
single persistent Fly volume mounted at `/data`; do not scale this deployment
past one Machine without moving to a network database.

```bash
fly volumes create trip_data --region iad --size 1 --app barrett-italy-2026
fly deploy
fly status
```

The container runs `alembic upgrade head` before starting the server. Health is
available at `/healthz`. Production sets `APP_PASSWORD` as a Fly secret; the
site and API use browser-native HTTP Basic authentication with username
`barrett`.

## Legacy source files

The old static site is retained under `italy-trip-2026/public/` as import history
only and is no longer copied into the Vite build (`publicDir: false`). The seed
imports `itinerary-data.js`, `adventures.csv`, `bikeparks.csv`, `costs.csv`, and
the normalized `tools/activities-seed.csv`. SQLite is authoritative after that
initial import.

The earlier multi-leg fare-search backend remains in `app/` for historical
compatibility, but is disabled in the production container and is no longer the
public home page.
