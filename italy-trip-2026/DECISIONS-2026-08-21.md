# Canonical facts · 21 Aug 2026

> ⚠️ **Superseded in part by [`DECISIONS-2026-08-30.md`](DECISIONS-2026-08-30.md)** (30 Aug 2026): lodging is **$9,262** not $8,955 (Rome was $308 light), trains are **€483 via a 4+2 split booking** not €561–788, and every activity is now priced for the party of six. `public/*.html` remains the source of truth.

**The HTML pages in `public/` are the source of truth.** The numbered markdown docs
(`01-` … `09-`) drifted badly and are being rebuilt from the site. When this file and a
page disagree, the page wins.

> **UPDATE — the car is now actually BOOKED, and the dates moved.** The reservation is
> **Budget, confirmation 02391839US2**, and the drop is **Thu Oct 15 at 12:00**, not Wed
> Oct 14 — **5 rental days, not 4.** The CAR section below has been rewritten to the real
> booking; the `public/` pages already carry it. Anything anywhere still saying "drop Oct 14"
> or "4 rental days" is stale.

## Trip shape (from `public/plan.html`)

Milan → Turin → Cinque Terre (Chiavari) → Florence → Rome → Venice/Lido → Dolomites → Malpensa.
**8 stops, 34 nights, Sep 11 – Oct 15 2026.** Family of six.

| # | Stop | Dates 2026 | Nts |
|---|------|-----------|-----|
| 1 | Milan | Sep 11–13 | 2 |
| 2 | **Turin** | Sep 13–… | — |
| 3 | Cinque Terre (**Chiavari** base) | … | — |
| 4 | Florence (work base) | … | — |
| 5 | Rome (work base) | … Oct 3 | — |
| 6 | **Venice / Lido** — Airbnb ✓ **booked**, next door to MuMu | **Oct 3–10** | **7** |
| 7 | **Dolomites (Val Gardena / Ortisei)** | **Oct 10–14** | **4** |
| 8 | **Casorate Sempione** — Osteria della Pista dal 1875 ✓ **booked** | Oct 14–15 | 1 |

Stop 8 is **settled**: **Hotel Osteria della Pista dal 1875, Via Verbano 1, 21011 Casorate
Sempione (VA)** — booked on Booking.com, **$406**, **9 minutes from MXP**, free airport shuttle,
restaurant on site, 450 m from Casorate Sempione station. The lake-town options (Orta San
Giulio, Stresa, Bergamo) were considered and dropped: each meant arriving at dusk and walking
six people and six bags into a car-free centre the night before a non-refundable transatlantic
flight. **The scenery moved to the drive instead** — see below.

Read the exact dates for stops 1–5 out of `public/plan.html` — do not invent them.

## LODGING IS 100% BOOKED (22 Aug 2026)

**All 8 bases, all 34 nights, $8,929.94.** No bed is outstanding. The final one was
**Venice/Lido — Airbnb `1151356839669861774`, Oct 3–10, 7n, $2,177, next door to MuMu**
(vs a $1,800 estimate → $377 over, and worth it: visiting Aunt Muriel is a core purpose
of the trip, and this puts us on her doorstep rather than a vaporetto ride away).

| Base | Nts | Booked |
|---|---|---|
| Milan · San Siro | 2 | $465.60 |
| Turin · Centro | 2 | $415.71 |
| Chiavari · Vista sul Carruggio | 4 | $547.06 |
| Florence · San Frediano (+Grandma) | 7 | $1,937.57 |
| Rome · Appio-Tuscolano | 7 | $1,977.00 |
| **Venice / Lido — next to MuMu** | 7 | **$2,177.00** |
| Dolomites · Singerhof, Kastelruth | 4 | $1,004.00 |
| Casorate Sempione · Osteria della Pista | 1 | $406.00 |
| **Total** | **34** | **$8,929.94** ($263/night) |

Consequence: **lodging is no longer a low/avg/high band anywhere.** `/housing` now shows
actuals, and `/budget`'s lodging row is a fixed $8,930 across all three columns — which
moved the in-country total to **≈$17.8K / $20.3K / $23.4K** and the honest band to **$18–25K**.
Confirmation amounts all live in `public/costs.csv`.

### Stops that NO LONGER EXIST
- **Lake Como** — cut. Replaced by **Turin**. Never was visited.
- **Bologna** — no longer an overnight stop. It is a **day trip from the Florence base**
  (Firenze S.M.N. → Bologna Centrale ~37 min Frecciarossa). See `public/bologna.html`.

### Celebrations (from `public/celebrations.html`)
- **Rhys turns 18 · Sep 18 · Ligurian coast** (not Florence) — seafood dinner over the Med.
- **Anniversary · Oct 9 · VENICE** — canalside dinner for two; boys have pizza night at the
  Lido place. (NOT in the Dolomites.)
- **Grey turns 12 · Oct 12 · Dolomites** — Seceda cable car → rifugio lunch → Kaiserschmarrn
  or strudel with a candle → pizza dinner in Ortisei.

## THE CAR — BOOKED ✓ (supersedes every page)

The old plan was: train Venice → Bolzano, collect a car in Bolzano, return it in Bolzano,
then train Bolzano → Verona → Milano Centrale → Malpensa Express. **All three parts are dead.**

**The actual reservation:**

| | |
|---|---|
| **Supplier** | **Budget** — **confirmation 02391839US2** · **+1 866-671-7282** |
| **Vehicle** | "**Standard-Size Van**" class — **Peugeot 5008 or similar · 7 seats · 4 bags · automatic** |
| **Included** | Unlimited mileage · collision damage waiver · theft protection · **free cancellation** |
| **Pick up** | **Sat Oct 10, 12:00** — Marco Polo Airport (VCE), Multipiano P1 terzo piano, Venice 30100 |
| **Drop off** | **Thu Oct 15, 12:00** — Malpensa Airport (MXP), Terminal 1, Milan 21010 |
| **Duration** | **5 rental days**, one-way |
| **Price** | **$717** all-in, incl. the one-way fee and taxes. Logged in `public/costs.csv` as **booked** — verify against the actual Budget charge. Fuel + autostrada tolls are separate, **~$185**. |

**The shape this creates — the subtle part:**
- **Wed Oct 14 is a scenic drive, not a transfer sprint and not a sightseeing day.** No museums,
  no castles, no queues — explicitly **not** Ötzi, MUSE, Sirmione or Bergamo. The route is
  A22 to **Riva del Garda**, then the cliff-carved **Gardesana Occidentale (SS45bis)** down
  Garda's west shore, a **long lunch at Gargnano**, then the A4 west. ~5h30 driving, one stop,
  parked at Casorate Sempione by ~16:30.
  *Fallback if the Riva–Limone stretch is shut for rockfall (check ANAS): A22 to Verona, A4 west.*
- **Thu Oct 15 morning still has a car.** The drop is at **noon**, four hours before the 16:20
  flight — but the point of the 9-minute hotel is that the morning is unhurried, not that it's
  usable for another outing.
- **The last night (Oct 14–15) is booked** — Osteria della Pista dal 1875, Casorate Sempione,
  **$406** (against a $170 penciled estimate — $236 over).

**The rest of the rationale, unchanged:**
- Pickup at VCE *replaces* the €152–180 Venezia S. Lucia → Bolzano rail leg entirely — a direct
  Alilaguna boat runs from the Lido to the airport, so no train, no bags through S. Lucia.
- The one-way drop at MXP *replaces* the €180–290 Bolzano → Milan → Malpensa Express rail leg.
- **Why a 7-seater:** six people need six belts, and Europe has no 6-seat class — the jump is
  5 → 7. With six aboard you fold one third-row seat for luggage. NOT a 9-seat van.
- **Why not Bolzano:** its depot had two 7+ seat offers total, both 9-seat vans at ~€1,150.
  Verona and VCE have deep inventory. Bolzano is a stockout risk.
- Net saving vs. the old train-in/train-out plan: roughly **€700**.

**Still outstanding, and unfixable abroad: the two International Driving Permits** (Dan and
Kei, ~$20 each at AAA). Italy requires an IDP alongside a US licence and the desk can refuse
the car without one. The car is booked; the permits are not.

## Lift dates — CONFIRMED 21 Aug 2026 (previously flagged "check this")

Several pages warn that Val Gardena's lifts "typically close mid-October." **That is wrong
for 2026** — it confuses the *Gardena Card* (which does end 11 Oct) with the lifts themselves.

| Lift | 2026 season | Source |
|---|---|---|
| Ortisei–Furnes–Seceda (both stages) | **22 May – 2 Nov** | seceda.it |
| Mont Sëuc (Ortisei → Alpe di Siusi) | to **2 Nov** | montseuc.it |
| Alpe di Siusi cableway (from Siusi) | to **1 Nov** | seiser-alm.it |
| Fermeda chairlift (ridge-top) | closes **20 Sep** — unavailable to us | seceda.it |
| Kronplatz Bike Park | to **8 Nov** | kronplatz.com |

**Oct 12 (Grey's birthday) is comfortably inside every one of these.** The "confirm the lift
dates" warnings on `/dolomites` and `/celebrations` can be closed out as resolved.

## Alpe di Siusi road rule — NEW

The road from Siusi up to Compatsch is **closed to private cars 09:00–17:00** (year-round while
the cableway runs). By day you go up on the Mont Sëuc cableway from Ortisei. **But it reopens
to cars after 17:00** — which makes a sunset dinner up at Compatsch (~1,850 m) possible on the
car leg. Sunset mid-October is ~18:30.

## The four-night squeeze

4 nights = **only three full days: Oct 11, 12, 13.** Oct 10 is a travel afternoon, Oct 14 is the
drive to Malpensa. Oct 12 is locked to Grey's birthday. So Kronplatz (Keir) and Jude's
rocks/minerals day take Oct 11 and Oct 13 — and **Alpe di Siusi has no slot left.** It is either
cut, or squeezed into the Oct 10 arrival afternoon if the drive goes quickly.

## Dan's work rhythm
Works **16:00–23:00 Italian time, Mon–Fri**. On the Dolomites leg that means:
- **Sat Oct 10, Sun Oct 11** — free.
- **Mon Oct 12** — must be blocked for Grey's birthday.
- **Tue Oct 13** — the only normal work evening; keep that day's plan close to base.
- **Wed Oct 14 and Thu Oct 15** — both need PTO (driving through the window, then flying).
  The 14th is the drive down to the Malpensa area; the 15th is car back at 12:00, fly 16:20.

## Repo hazards
- `tools/build-adventures.mjs` reads from a scratchpad path belonging to a **dead session**
  (`7707d7f7-…`) that no longer exists. **The pipeline cannot be re-run.**
  `public/adventures-data.js` is now hand-edit-only. Do not attempt `node build-adventures.mjs`.
- Do not edit `public/adventures-data.js`, `public/bikeparks-data.js`, or `public/costs-data.js`
  as part of the doc rebuild.
