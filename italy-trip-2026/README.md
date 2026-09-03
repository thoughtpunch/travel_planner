# Italy 2026 frontend

This directory contains the React frontend for the family trip wiki. The trip is
booked; the UI is an operational reference for dates, transport, stays,
activities and costs.

The FastAPI service owns all mutable data. In development, Vite proxies `/api`
to `http://127.0.0.1:8000`. In production, `npm run build` writes the frontend to
`../app/static/wiki-dist`, where FastAPI serves it.

```bash
npm ci
npm run dev
```

The legacy files in `public/` are retained only as seed/import history. Vite has
`publicDir: false`, so those old planning pages and their commentary are not
part of the deployed site. After initial import, SQLite is authoritative.

Primary routes:

- `/` — confirmed trip overview
- `/itinerary` — dated trip, including scheduled activities
- `/activities` — choose, schedule, cost and attach confirmations
- `/costs` — shared ledger; activity cancellations and refunds sync both ways
- `/costs` — editable trip ledger

See the repository root `README.md` for schema, migrations and Fly deployment.
