# 03 — Routes & Transit

> ⚠️ **Superseded in part by [`DECISIONS-2026-08-30.md`](DECISIONS-2026-08-30.md)** (30 Aug 2026): lodging is **$9,262** not $8,955 (Rome was $308 light), trains are **€483 via a 4+2 split booking** not €561–788, and every activity is now priced for the party of six. `public/*.html` remains the source of truth.

> Rebuilt 21 Aug 2026 from the deployed site (`public/trains.html`, `public/plan.html`,
> `public/dolomites.html`). The HTML pages are the source of truth; where this doc and a
> page disagree, the page wins. **The rental car is now booked** — Budget ref
> **02391839US2**, VCE Oct 10 12:00 → MXP Oct 15 12:00, **5 days** — and this doc is
> synced to it.

## The big picture

34 nights, **8 stops**, Sep 11 – Oct 15 2026, family of six. It is a **rail loop that starts and ends at Malpensa**, with **one rental car** at the end. No internal flights, no ferries between regions this year. Italian rail — Frecciarossa/Italo where speed pays, flat-fare Regionale everywhere else — does all the heavy lifting, and then the car does the last two moves in one go.

```
        ┌──────────────────── rail ────────────────────┐
  Milan ───► Turin ───► Chiavari ───► Florence ───► Rome
 (Sep 11)   (Sep 13)    (Sep 15)      (Sep 19)    (Sep 26)
                                          │           │
                            Bologna ◄─────┘           │ rail
                        (day trip, 37 min)            ▼
                                               Venice / Lido
                                                  (Oct 3)
                                                      │
                                        Alilaguna Lido ─► VCE
                                        pick up the car · Sat Oct 10
                                                      ▼
  Malpensa area ◄═ car · ~370 km ═════ Dolomites / Ortisei
  (Wed Oct 14 · drive down,               (Oct 10–14)
   sleep near MXP with the car —
   location TBD)
        │
        ▼
  MXP · Thu Oct 15 — drop the car at Terminal 1, 12:00 · fly home 16:20

  ───►  rail          ═══►  the one car leg
```

| # | Stop | Dates 2026 | Nts |
|---|------|-----------|-----|
| 1 | Milan (arrival) | Sep 11–13 | 2 |
| 2 | Turin | Sep 13–15 | 2 |
| 3 | Ligurian Coast — **Chiavari** base | Sep 15–19 | 4 |
| 4 | Florence (work base) | Sep 19–26 | 7 |
| 5 | Rome (work base) | Sep 26–Oct 3 | 7 |
| 6 | Venice / Lido | Oct 3–10 | 7 |
| 7 | Dolomites (Val Gardena / Ortisei) | **Oct 10–14** | 4 |
| 8 | Near Malpensa — **location TBD** (airport hotel, or a lake town within ~1h) | Oct 14–15 | 1 |

**Lake Como is cut** — Turin replaced it; we never go to the lake. **Bologna is not an overnight stop** — it is a day trip from the Florence base.

See the live **[/trains](public/trains.html)** page for the same legs with links to buy, and **[/plan](public/plan.html)** for the map.

## Two kinds of train, two kinds of ticket

Get this and everything else is easy — Italy runs two different products with different buying rules.

- **Le Frecce / Italo — high-speed.** Fast, reserved, seat-assigned (Frecciarossa is Trenitalia; Italo is the private competitor on the same routes). Price is **dynamic, like flights**: a Florence→Rome seat is ~€19 a month out and ~€55 the day of. **Book these early** — the cheap "Super Economy" fare sells in tiers and is gone once the train fills. We use high-speed for **Milan→Turin, Florence→Rome, Rome→Venice**, and for the **Bologna day trip** out of Florence.
- **Regionale — the local network.** Flat price, never sells out, no reservation, no assigned seat. Buy it five minutes or five weeks ahead — same fare. This is how we ride **Genoa→Chiavari**, the **Cinque Terre Express** coast line, and the short hops. One rule: paper tickets must be **validated/self-checked-in** before boarding (app tickets auto-activate). Slower, but on our short legs the time difference is tiny and the saving is real.

## The family discount — "Offerta Famiglia"

On Le Frecce and Intercity, a group of **2–5 that includes at least one child under 15** travels as a family: the **under-15s ride FREE and the adults get 20% off**. **Grey (11, turns 12 on Oct 12) and Keir (9)** are both under 15.

Because a family booking maxes at **5 people**, we **split the six into two bookings, each carrying one of the little ones** — e.g. {Dan · Kei · Grey} and {Rhys · Jude · Keir} — so both bookings unlock the discount. Rhys (18) and Jude (16) pay adult fares. Italo has the same mechanic ("Italo Famiglia"). Set the passenger ages when booking and it applies automatically.

## The 5 rail legs, in travel order

The doc used to claim eight rail legs. It is **five**. Two of the old ones (Venice→Bolzano, and Bolzano→Verona→Milan→Malpensa Express) were killed by the car decision below; the other missing ones were legs to stops that no longer exist.

Relocations are mostly Sat/Sun (the first week is PTO, so midweek moves are fine there). Dan works 4–11pm, so we travel mornings/early afternoons. **All fares below are a real Aug 2026 pull of the cheapest advance tickets for all six of us — not estimates**, with the Famiglia discount applied on the high-speed legs.

| # | Leg · date | Line & operator | Time | Family of 6 (Aug 2026 pull) | Book |
|---|---|---|---|---|---|
| 1 | **Milan → Turin** · Sun Sep 13 | Frecciarossa / Italo · Milano Centrale → Torino Porta Nuova (direct, frequent) | ~1 h | **from €77** | **Book early — dynamic** |
| 2 | **Turin → Chiavari** (via Genoa) · Tue Sep 15 (PTO) | Torino P. Nuova → Genova P. Principe (~1h45), **submarine + sea-museum stop in Genoa**, then Genova → Chiavari (~40 min Regionale) | ~2½ h | **from €91** | 1 change at Genoa |
| 3 | **Chiavari → Florence** · Sat Sep 19 | Regionale Veloce / Intercity · Chiavari → Firenze S.M.N. (change at La Spezia/Pisa, or via Genoa) | ~2½ h | **from €118** | Flat/reserved regional |
| 4 | **Florence → Rome** · Sat Sep 26 | Frecciarossa / Italo · Firenze S.M.N. → Roma Termini (direct) | ~1 h 35 | **from €99** | **Book early — dynamic** |
| 5 | **Rome → Venice** · Sat Oct 3 | Frecciarossa / Italo · Roma Termini → Venezia S. Lucia (direct) — then vaporetto to the Lido | ~4 h | **from €176**<br>(direct Freccia €221.40) | **Book early — dynamic** |

**Five legs = ~€561 for all six** at the cheapest fares pulled. Take the **direct** 4h Frecciarossa to Venice instead of the €176.40 / 6h18 one-change slog — worth the €45 with four boys and packs — and the five legs land at **~€606**.

> The `/trains` page still quotes **~€714** for "six core legs." That number includes the old **Venice→Bolzano** rail leg (€151.80–179.70), which the car decision deletes. Subtract it and you get the €561 above.

**Legs 1, 4 and 5 are the dynamic-priced fast ones — book them the moment fares open (~4 months out), with passenger ages set so Famiglia applies.** That is where the real money is. Legs 2 and 3 are flat-fare Regionale you can buy same-week without penalty.

### Plus one day trip: Bologna

Bologna is **no longer an overnight stop**. From the Florence base, **Firenze S.M.N. → Bologna Centrale is ~37 min by Frecciarossa** (~€30–50pp walk-up, cheaper booked ahead — or take Regionale if the Freccia fare spikes that day). Go for the day — tortellini, tagliatelle, mortadella, the porticoes — and be home for Dan's 4pm work window. Jude's **Motor Valley** (Lamborghini / Ferrari / Ducati) is an optional add-on from Bologna. See [/bologna](public/bologna.html).

## The one car leg — Dolomites + the run home, Oct 10–15 · BOOKED ✓

**Budget · confirmation 02391839US2 · +1 866-671-7282.** The old plan — train Venice → Verona → Bolzano, collect a car in Bolzano, return it in Bolzano, then train Bolzano → Verona → Milano Centrale and take the Malpensa Express out to the airport — is **dead in all three parts.**

**One car, picked up at one airport and dropped at another:**

| | |
|---|---|
| **Pick up** | **Sat Oct 10, 12:00** — Marco Polo Airport (VCE), Multipiano P1 terzo piano, Venice 30100 |
| **Drop off** | **Thu Oct 15, 12:00** — Malpensa Airport (MXP), Terminal 1, Milan 21010 |
| **Duration** | **5 rental days**, one-way |
| **Vehicle** | "Standard-Size Van" class — **Peugeot 5008 or similar · 7 seats · 4 bags · automatic** |
| **Included** | Unlimited mileage · CDW · theft protection · **free cancellation** |
| **Price** | **$717** all-in (one-way fee + taxes included), **plus ~$185** fuel and autostrada tolls |

- Getting to the car: a direct **Alilaguna** boat runs from the Lido to VCE, so there is no train and no hauling six people's bags across to S. Lucia. This **replaces the €152–180 Venezia S. Lucia → Bolzano rail leg entirely.**
- The one-way drop at MXP **replaces the €180–290 Bolzano → Verona → Milan → Malpensa Express rail leg.**
- **The drop is Thu Oct 15, not Wed Oct 14 — that reshapes the last two days.** We drive Ortisei → the Malpensa area on **Wed Oct 14**, **sleep near the airport that night with the car**, and hand it back at noon on flight day, **four hours before the 16:20 departure**. Oct 14 becomes a driving/sightseeing day rather than a transfer sprint, and **Thursday morning still has a car** — Volandia at the airport, or a run out to Lake Maggiore.
- **The last night (Oct 14–15) is near Malpensa, location TBD** — an airport hotel, or a lake town on Maggiore / Orta within ~1h. The car makes either workable; it hasn't been decided.
- **Net saving vs. the old train-in / train-out plan: roughly €700.**

### Why not Bolzano

Bolzano's depot had **two 7+ seat offers total, both 9-seat vans at ~€1,150**. That is a stockout risk on a small-city counter with a family of six and no plan B. **Verona and VCE have deep inventory.** Picking up at a major airport is the whole point.

### Why a 7-seater, not a van

**Six people need six belts, and Europe has no 6-seat class — the jump is 5 → 7.** So the target is a 7-seat crossover/MPV: **Peugeot 5008 / Škoda Kodiaq / VW Touran / SEAT Tarraco** class. With six aboard you **fold one third-row seat down for luggage**, which is exactly enough given we're travelling carry-on only. **Not a 9-seat van** — bigger, dearer, worse on mountain switchbacks and in village parking.

### The drive home: Ortisei → the Malpensa area (Wed Oct 14)

**~370 km, ~4h30, motorway essentially the whole way** (Val Gardena down to the A22 at Bolzano, south to Verona, then west on the A4). Break it with a **lunch stop at Sirmione on Lake Garda** — it sits right on the route and turns a transit day into a last good afternoon. Wed Oct 14 needs PTO; the drive runs through Dan's work window. **There is no rush at the far end** — the car isn't due back until noon the next day, so the arrival is into wherever we're sleeping, not into a rental return queue.

### Driving rules to know

- 🔴 **International Driving Permit (IDP) is required** to drive in Italy on a US licence — **one each for Dan and Kei, and this is the outstanding car-related to-do.** ~$20 at AAA, over the counter, bring a passport photo and your licence. It is a paper booklet issued alongside the licence, not a replacement for it, and **it cannot be obtained in Italy** — the rental desk can refuse the car without one.
- **ZTL** — *zona a traffico limitato*. Nearly every Italian old town centre has one, cameras enforce it automatically, and the fine arrives months later via the rental company (plus their admin fee). Do not drive into a historic centre. Park outside and walk.
- **Autostrada tolls** — take a ticket on entry, pay on exit (card works). Or ask about **Telepass** at the counter. Budget roughly €35–45 in tolls for the Ortisei→MXP run, plus fuel — **~$185 together**, and separate from the $717 rental.
- **Alpe di Siusi road rule** — the road from Siusi up to Compatsch is **closed to private cars 09:00–17:00**. By day you go up on the **Mont Sëuc cableway from Ortisei**. It **reopens to cars after 17:00**, which makes a sunset dinner up at Compatsch (~1,850 m) genuinely possible — mid-October sunset is ~18:30.

### What it costs

| Component | Amount | Status |
|---|---|---|
| Rental — **5 days, VCE → MXP one-way**, incl. one-way fee and taxes | **$717** | **BOOKED** (Budget ref 02391839US2) |
| Fuel + autostrada tolls | **~$185** | estimate |
| **Car leg, all-in** | **~$902** | |

The $717 is the price actually booked, not a quote — it's on the `/costs` ledger as booked, with a note to **verify it against the real Budget charge** when it posts.

> The `/budget` model still carries a **$650 / ~5 days from Bolzano** line for the car. That needs re-basing to **$902** — but the two rail legs the car replaces come *out* of the trains line (−€332–470), so the ground total still moves down, not up.

## Local transit inside each stop

- **Milan (Sep 11–13)** — base is **San Siro**, a short walk from M5 *San Siro Stadio* and several trams. For the whole family in one vehicle, **Free Now** (the Lyft-powered taxi app) has 6-seat vans for ~€15–20 into the centre, which beats splitting up on the metro with jetlag.
- **Turin (Sep 13–15)** — base by **Porta Nuova**; foot, tram and metro do everything. Metro to **Lingotto** for the rooftop test track; tram/bus to Sassi then the 1884 **rack railway up to Superga** (check running days).
- **Ligurian Coast · Chiavari (Sep 15–19)** — the **Cinque Terre Card (Treno)**: unlimited local trains Levanto↔La Spezia through all five villages, plus trail access, buses and wifi, ~€19.50/day adult with kid discounts (1- or 2-day). Ride the Regionale up from Chiavari to Levanto/Monterosso first; the **Cinque Terre Express** then runs every ~20 min. Camogli → San Fruttuoso is a **boat**, good-weather day only.
- **Florence (Sep 19–26)** — a walking city from a central-ish base; the only real transit spend is the **Bologna day trip** (above).
- **Rome (Sep 26–Oct 3)** — base is **Appio-Tuscolano on Metro A**. Metro A/B/C, trams and buses; walking for the centro. **Colosseo/Fori Imperiali on Line C opened 16 Dec 2025 and San Giovanni is the A↔C interchange**, so the ancient core is ~10 minutes from the base with one change. Watch the clock: **last metro is 23:30 Sun–Thu** (01:30 Fri/Sat), after which the **nMB night bus** covers the Line B corridor.
- **Venice / Lido (Oct 3–10)** — ACTV **vaporetti** are the water buses. From the Lido base we ride daily, so a **multi-day ACTV pass** (2/3/7-day) beats €9.50 singles fast and covers Murano/Burano/Torcello; under-6s free. The Lido itself is flat, bike-and-foot. On **Oct 10 take the Alilaguna direct to VCE** for the car.
- **Dolomites (Oct 10–14) and the last two days** — the car (above), which is ours through to noon on Oct 15, plus lifts: **Ortisei–Furnes–Seceda runs to 2 Nov, Mont Sëuc to 2 Nov, the Alpe di Siusi cableway to 1 Nov, Kronplatz Bike Park to 8 Nov** (2026 dates, confirmed 21 Aug 2026). Only the **Fermeda ridge-top chairlift closes 20 Sep** and is unavailable to us. Grey's Oct 12 birthday is comfortably inside every one of the others — the old "confirm the lifts before Oct 10" warning is resolved; it was confusing the *Gardena Card* (which does end 11 Oct) with the lifts.
- **Airport ends (Malpensa)** — **arrival Fri Sep 11, landing 21:55.** Either the **Malpensa Express** to Milano Centrale/Cadorna (~50 min, €13pp, runs past midnight) or, easier at that hour with six and bags, a **pre-booked 6-seat van** (~€100–120). Book the van; save the train for daylight. **Departure:** we drive down on Wed Oct 14 and sleep **near Malpensa with the car — location TBD (an airport hotel, or a lake town within ~1h)**, 2 rooms. Thursday morning we still have the car; it goes back at **MXP Terminal 1 at 12:00**, and the 16:20 flight home is a relaxed roll to the terminal. No shuttle dependency, no dawn scramble.

## Rough total

- **5 rail legs: ~€561** for all six at the cheapest advance fares pulled Aug 2026 — **~€606** taking the direct Frecciarossa to Venice. (Walk-up would be multiples of this; the Frecce legs are where the swing is.)
- **Bologna day trip: ~€120–250** for six, less if booked ahead with Famiglia.
- **The car leg: ~$902** — **$717 rental, booked** (5 days, one-way VCE→MXP, incl. fees and taxes) plus **~$185** fuel and tolls.
- **Local transit: ~$650–1,100** across the trip — vaporetti, the Cinque Terre Card, coast Regionali, Genoa, Rome Metro — per the [/budget](public/budget.html) bands.
- **Malpensa arrival van: ~€100–120**, one-off.

Rail plus local transit lands around **$1,400–2,000** all-in, with the car leg's **~$900** sitting beside it — and roughly **€700 less** than the old Bolzano train-in/train-out shape.

## Book in this order

1. **The dynamic Frecciarossa legs — Milan→Turin, Florence→Rome, Rome→Venice —** the day fares open (~4 months out), with passenger ages set so Famiglia applies. Biggest single saving on the whole transit budget.
2. ~~The car~~ **BOOKED ✓** — Budget, ref **02391839US2**, 7-seat automatic (Peugeot 5008 or similar), **VCE Sat Oct 10 12:00 → MXP Thu Oct 15 12:00**, 5 days, $717, free cancellation, Budget **+1 866-671-7282**. In its place, the remaining car task: 🔴 **two IDPs from AAA** (Dan + Kei, ~$20 each) — the one item that cannot be fixed once abroad.
3. **The Malpensa arrival van** for the 21:55 landing on Fri Sep 11 — late-night 6-seat transfers sell out.
4. **The Regionale legs** — Turin→Chiavari (via Genoa) and Chiavari→Florence — same-week, no rush, flat fares. Same for the **Bologna day trip** unless the Freccia fare is worth locking.
5. **On arrival, in each place:** the Cinque Terre Card at any coast station, and a multi-day ACTV vaporetto pass on the Lido.
