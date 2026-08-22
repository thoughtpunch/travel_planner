# 04 — Budget

> Rebuilt 21 Aug 2026 from `public/budget.html`, `public/costs.html` / `costs-data.js`,
> `public/trains.html` and `public/housing.html`. The HTML pages are the source of truth.
> The **car is now booked** — Budget ref **02391839US2**, **$717** for **5 days**,
> VCE Oct 10 12:00 → MXP Oct 15 12:00 — and this doc carries that real number, not the old
> 4-day estimate. Every place the pages disagree with each other is flagged inline rather
> than quietly resolved.

## Headline: ~$20K in-country average

A bottom-up model of every dollar spent **inside Italy** across the locked **8-stop loop** —
lodging, food, activities, local transit, the **5 remaining intercity rail legs**, the
**Dolomites rental car**, and a contingency. Family of 6 (2 adults + 4 boys, two of them
teenagers who eat like adults), **34 nights, Sep 11 – Oct 15, 2026**.

| Case | In-country total | Read as |
|---|---|---|
| Low | **$16K** | Levers pulled, lean weeks |
| **Average** | **$20K** | The realistic plan |
| High | **$25K** | Peak prices, splurges in |

- **~$594/day** for the family, in-country
- **~$99/person/day**
- Honest all-in band: **$18–26K** ground cost in Italy

> **Flights are BOOKED & PAID at $5,346 — and sit OUTSIDE this number.**
> The round-trip air (Icelandair both ways via Keflavík, ref **AMBVO4** — depart BWI 23:20
> Thu Sep 10, land MXP 21:55 Fri Sep 11; home from MXP 16:20 Thu Oct 15) is already booked
> and paid at **$5,346**. It is *not* in any line on this page. Everything below is money
> spent **after you land**. Never fold the flights into the ground budget.
>
> The fare is Economy Light (1 carry-on each, 0 checked bags) — **by design, we travel
> carry-on only**, so there are no baggage add-ons to buy. Nothing extra to budget here.

"Average" assumes whole-place lodging on weekly rates, cooking 4–5 nights a week, and leaning
on Italy's under-18-free museum access. These are estimates, not quotes.

## The trip this is priced against

Eight stops, 34 nights, dates straight off `public/plan.html`:

| # | Stop | Dates 2026 | Nts |
|---|---|---|---|
| 1 | Milan · arrival | Sep 11–13 | 2 |
| 2 | Turin | Sep 13–15 | 2 |
| 3 | Ligurian Coast · base **Chiavari** | Sep 15–19 | 4 |
| 4 | Florence · work base | Sep 19–26 | 7 |
| 5 | Rome · work base | Sep 26–Oct 3 | 7 |
| 6 | **Venice / Lido** | **Oct 3–10** | **7** |
| 7 | **Dolomites (Kastelruth)** | **Oct 10–14** | **4** |
| 8 | Near Malpensa · departure — **location TBD** (airport hotel, or a lake town within ~1h) | Oct 14–15 | 1 |

**Lake Como is cut** — Turin replaced it, and no Como/Brunate cost belongs anywhere in this
model. **Bologna is not an overnight** — it is a **day trip from the Florence base**
(Firenze S.M.N. → Bologna Centrale, ~37 min Frecciarossa), and its rail cost sits inside the
intercity-rail bucket, not lodging.

## The seven buckets

Everything on the ground, grouped, each with a low / average / high band. Lodging comes
straight off the housing model; the rest is built from family-of-6 day rates and the
specifics of this itinerary.

| Bucket | Low | Avg | High | What's in it |
|---|---|---|---|---|
| Lodging | $7,500 | **$9,200** | $10,800 | Whole-place sleeps-6 apartments; weekly rate on the three 7-night bases (Florence, Rome, Venice/Lido); the Kastelruth farmhouse ✓ booked at $1,004; the last night near Malpensa, location TBD (2 rooms, 1 nt) |
| Food | $4,300 | **$5,200** | $6,300 | Groceries + dining. Cook / eat in 4–5 nights a week; 3 splurge dinners for the celebrations |
| Activities & entry | $900 | **$1,300** | $1,800 | Classes, workshops, boats, cable cars (Seceda, Mont Sëuc), Kronplatz bike park. Under-18s free at Italian state museums |
| Local transit | $650 | **$850** | $1,100 | Venice vaporetti (7-day ACTV from the Lido), Cinque Terre Card + coast regionali, Genoa transit, Rome Metro B, the **Alilaguna boat Lido → Marco Polo** on Oct 10 |
| Intercity rail — **5 legs** + Bologna day trip | $850 | **$1,150** | $1,550 | The 5 rail moves that survive the car decision, plus the Bologna food day-trip from Florence — detail on the Trains page |
| Rental car — **BOOKED, 5 days, VCE → MXP one-way** | $880 | **$902** | $950 | 7-seat automatic picked up at Venice Marco Polo **Oct 10 12:00**, dropped one-way at Malpensa T1 **Oct 15 12:00**: **$717 booked** incl. the one-way fee and taxes, plus **~$185** fuel + autostrada tolls. Only the fuel/tolls half is still a band |
| Misc / contingency | $1,200 | **$1,600** | $2,300 | SIMs, laundry, gifts/souvenirs, medical/pharmacy, the inevitable unplanned |
| **In-country total · 34 nts** | **≈ $16,280** | **≈ $20,200** | **≈ $24,800** | |
| Per day | $479 | $594 | $729 | |
| Per person, per day | $80 | $99 | $122 | |

Lodging and food together are **~70%** of the ground cost — which is exactly why the
whole-place-with-a-kitchen strategy is the whole ballgame. The car is now the third-biggest
lumpy line after rail, and it is no longer a rounding error.

### Lodging, checked against what's actually booked

Five of the eight stays are booked with real numbers (from the `/costs` ledger):

| Stay | Amount | Status |
|---|---|---|
| Milan · Sep 11–13 (San Siro Airbnb) | $465.60 | booked |
| Turin · Sep 13–15 (Centro Airbnb) | $415.71 | booked (free cancellation) |
| Chiavari · Sep 15–19, 4n (Vista sul Carruggio) | $547.06 (€506.54) | booked |
| Florence · Sep 19–26, 7n (San Frediano, +Grandma) | $1,937.57 | booked |
| Rome · Sep 26–Oct 3, 7n | $1,977.00 | booked |
| Venice / Lido · Oct 3–10, 7n | $1,800 | estimate |
| Dolomites / Singerhof, Kastelruth · Oct 10–14, 4n | **$1,004** | **booked** |
| Last night near Malpensa · Oct 14–15, 1n — **location TBD** | $170 | estimate |
| **Total** | **≈ $8,713** | 61% committed |

That lands **just under the $9,200 average** in the table above and comfortably inside the
housing page's €7,000 / €8,500 / €10,000 (≈ $7,560 / $9,180 / $10,800) band. The two open
estimates are the ones with room to move: the housing model's own average for **Venice/Lido
is €1,960 ≈ $2,117**, i.e. **~$300 above** the $1,800 placeholder in the ledger. Budget the
Venice week nearer $2,100 than $1,800.

## The car — BOOKED ✓

**Budget · confirmation 02391839US2 · +1 866-671-7282.** The old shape — train Venice → Bolzano,
rent in Bolzano, return in Bolzano, train Bolzano → Verona → Milano Centrale → Malpensa Express —
is **dead in all three parts.**

| | Old shape | What's actually booked |
|---|---|---|
| Get to the mountains | Rail Venezia S. Lucia → Verona → Bolzano, **€152–180** for six | **Alilaguna boat Lido → Marco Polo**, collect the car at **VCE, Sat Oct 10 12:00** (Multipiano P1, terzo piano) |
| The car | Bolzano depot, ~5 days. Real inventory there: **two 7+ seat offers, both 9-seat vans at ~€1,150** | **5 days, Oct 10 → Oct 15.** "Standard-Size Van" class — **Peugeot 5008 or similar, 7 seats, 4 bags, automatic**; unlimited mileage, CDW, theft protection, free cancellation |
| Get to the plane | Return car in Bolzano, rail Bolzano → Verona → Milan → Malpensa Express, **€180–290** for six | **Drive Kastelruth → the Malpensa area Wed Oct 14, ~355 km, ~4h15**, sleep near MXP with the car, **one-way drop at MXP Terminal 1, Thu Oct 15 12:00** |

**The car line, built up from the real booking:**

| Component | Amount | Status |
|---|---|---|
| 5-day 7-seat automatic, VCE → MXP one-way, all-in | **$717** | **BOOKED** — includes the one-way fee and taxes. On the `/costs` ledger as booked, with a note to **verify against the actual Budget charge** |
| Fuel + autostrada tolls | **~$185** | estimate — ~370 km of motorway plus the mountain driving |
| **Total** | **~$902** | banded **$880 / $902 / $950** — the rental half is now fixed, so only the fuel/tolls half can move |

**Don't model this line as a day rate.** Roughly **$350 of the total is fixed one-way fee plus
taxes**; the extra fifth day cost far less than a fifth of the total, which is exactly why
keeping the car through to flight-day noon was worth it.

### Why the car line goes UP while the plan saves money

This is the reconciliation that matters, and it is easy to get wrong:

- **The old $650 budget line was fiction.** It assumed a normal 5-day rental out of a Bolzano
  depot that, when actually checked, had **only 9-seat vans at ~€1,150**. Six people need six
  belts and Europe has no 6-seat class — the jump is 5 → 7 — so a "cheap 6-seater in Bolzano"
  was never on the menu. Bolzano was also a stockout risk; VCE and Verona have deep inventory.
- **What the model gains:** the car line rises **+$252** at the average ($650 → $902).
- **What the model loses:** the two rail legs vanish entirely — **€332–470 ≈ $360–510**.
- **Net effect on this budget: about −$108 to −$258.** Small, because the old car line was
  understated by roughly the same amount the rail legs saved.
- **`DECISIONS-2026-08-21.md` books the saving at ~€700.** That figure is measured against
  what Bolzano would *really* have cost — the €1,150 van **plus** both rail legs — not against
  the too-low $650 line in the old budget. Both statements are true; they use different
  baselines. ⚠︎ *The exact €700 is not reproducible from the numbers published on the site;
  a bottom-up read gives €700–950 depending on which Bolzano car you assume.*

Two knock-on effects worth banking:

- **No hauling six people and bags through S. Lucia** on a Saturday — the Alilaguna goes
  straight from the Lido to the airport door. That boat fare belongs in **local transit**.
- **The Alpe di Siusi road** (Siusi → Compatsch) is closed to private cars **09:00–17:00** but
  **reopens after 17:00** — with the car on hand, a sunset dinner at Compatsch (~1,850 m,
  sunset ~18:30 in mid-October) is newly possible. Price it into food/activities if you take it.
- **We keep the car overnight on Oct 14 and hand it back at noon on Oct 15**, so there is **no
  airport-shuttle line and no separate transfer to buy** on the last day — and **Thursday morning
  is mobile**, which is a free half-day the old plan didn't have. It also means the last night
  doesn't have to be an airport hotel: **anywhere within ~1h of MXP (Lake Maggiore, Lake Orta)
  prices into the same lodging line**, and lake-town rooms often come in under airport rates.

## The rail, after the car decision

**Five intercity legs survive.** These are real cheapest-advance fares pulled in Aug 2026, not
guesses — family of six, Offerta Famiglia applied on the high-speed legs:

| Leg · date | Type | Family of 6 |
|---|---|---|
| **Milan → Turin** · Sun Sep 13 | Frecciarossa / Italo, ~1 h | from **€77** |
| **Turin → Chiavari** (via Genoa) · Tue Sep 15 | Freccia + regionale, ~2½ h | from **€91** |
| **Chiavari → Florence** · Sat Sep 19 | Regionale Veloce / Intercity, ~2½ h | from **€118** |
| **Florence → Rome** · Sat Sep 26 | Frecciarossa / Italo, ~1 h 35 | from **€99** |
| **Rome → Venice** · Sat Oct 3 | Frecciarossa / Italo, ~4 h | from **€176** (direct Freccia ~€221) |
| **Total, 5 legs** | | **€561 ≈ $606** |

**Deleted from the rail budget:** Venezia S. Lucia → Bolzano (**€152–180**) and
Bolzano → Verona → Milan → Malpensa Express (**€180–290**). Neither is happening. Any figure
that still counts them is stale.

On top of the €561 sits the **Bologna food day-trip from Florence** — Frecciarossa ~37 min,
~€30–50pp walk-up and cheaper booked ahead, so call it **€150–300 round-trip for six**
depending on Freccia vs. Regionale. That, plus dynamic-fare drift if the Frecce aren't booked
early, is the whole span between the $850 low and the $1,550 high.

⚠︎ **`trains.html` is mid-update and currently self-contradictory.** Its masthead now reads
"**5 rail legs · 1 car leg**" and "**the 5 rail legs ~€561** (pulled Aug 2026)" — which agrees
with the figure used here — and its last two table rows have been rewritten to the Alilaguna
boat / VCE pickup and the Kastelruth → MXP drive. But the same page still carries the old section
heading "**The 7 rail legs**", the old rough-all-in callout ("the six core rail legs …
**~€714**" plus "the final Dolomites→Malpensa leg … ~€180–290", i.e. **~$1,400–2,200**), the
old "Collect in **Bolzano** … 6-seater" airport card, and a booking checklist that still says
"Bolzano pickup/return, 6-seater" and "buy Venice→Bolzano same-week". **€714 − €152 = €561**,
so the header is right and the callout is stale; take the €561.

## Money-saving levers

Ranked by dollars saved. None of these cut anything you'd actually miss — they're the
difference between the high case and the low.

| Lever | How | Saves |
|---|---|---|
| **Weekly-rate lodging** | Book the three **7-night bases — Florence, Rome and Venice/Lido** — whole-place to trigger the weekly discount (10–20% off nightly), with a kitchen everywhere. Chiavari (4n) and Val Gardena (4n) get part of the way there; the 2-night Milan and Turin legs won't, so optimize those for *position* next to the station instead | $1,000–1,800 |
| **Cook 4–5 nights/week** | A restaurant dinner for six runs ~$130, a cooked one ~$40 — every home dinner nets ~$90–100. Shop Lidl / Eurospin / Conad and the markets (Mercato Centrale, Testaccio, the Bologna Quadrilatero, Rialto), not tourist alimentari | $1,200–1,800 |
| **Under-18s free at Italian state sites** | **Grey (11, 12 on Oct 12), Keir (9), Jude (16) and Rhys until Sep 18** walk into the Colosseum, Uffizi, Doge's Palace, Accademia and every state site **free**. Pay only for private experiences — classes, boats, cable cars. Rhys pays adult from his 18th | $500–800 |
| **Offerta Famiglia on the high-speed legs** | On Le Frecce and Intercity, a group of **2–5 including at least one under-15** travels as a family: **under-15s ride free, adults get 20% off**. Grey and Keir both qualify. A family booking maxes at 5, so **split the six into two bookings, each carrying one of the little ones** — e.g. {Dan · Kei · Grey} and {Rhys · Jude · Keir} — so both unlock it. Set passenger ages at booking and it applies automatically; Italo has the same offer ("Italo Famiglia"). Stack with early Frecce fares and Regionale on the short hops | $400–700 |
| **Passes, not singles** | A **7-day ACTV vaporetto pass** on the Lido crushes €9.50 singles; the **Cinque Terre Card (Treno)** bundles the coast trains, trails and buses (~€19.50/day adult, discounted for kids). Buy the pass the moment you'll ride more than twice | $200–400 |
| **Self-cater the Dolomites** | The chalet leg is meant to cost — but a kitchen plus a supermarket run in Ortisei keeps the priciest region from running away. Blow out on Grey's birthday dinner; groceries the rest | $300–500 |

Pull the top four and you're at the low case: weekly rates + cook 4–5 nights + under-18-free +
smart trains is the difference between the **$25K high** and the **~$16–18K low** — with
nothing cut from the trip. Layer on the card/FX game (dining multipliers, a Wise EUR balance
for groceries) for a few hundred more back.

⚠︎ `budget.html`'s lever card names this rail discount "**Bimbi Gratis**" while `trains.html`
describes "**Offerta Famiglia**" with the correct 2–5 / under-15-free / adults-−20% mechanics.
Offerta Famiglia is the one to book against. `budget.html` also lists only "Grey, Keir and
Rhys" as free at state museums and **omits Jude (16)** — the under-18 exemption at Italian
state sites is by age, so Jude is free too. Treated as an omission on the page, not a rule.

## Where to splurge

Cooking most nights buys three dinners worth blowing out. They're already inside the food
band — this is just where they land.

| Splurge | When / where | Why |
|---|---|---|
| **Rhys turns 18** | **Sep 18 · Ligurian coast** | Seafood dinner over the Mediterranean on the last coast night (his first legal aperitivo was up in Turin). Also his **last day of free state-museum entry** — time the big-ticket sites before it |
| **Anniversary** | **Oct 9 · VENICE / the Lido** | A canalside dinner for two during the unhurried week with MuMu; the boys get pizza night at the Lido place |
| **Grey turns 12** | **Oct 12 · Dolomites** | Seceda cable car → rifugio lunch → Kaiserschmarrn or strudel with a candle → pizza dinner in Ortisei |
| **The Val Gardena chalet** | **Oct 10–14** | The one deliberately-spent-up-on stay — priciest region, and the only leg with a car, so off-the-line is fine. A kitchen keeps the rest of the leg tight |

**Not** Florence for Rhys (that was the old plan) and **not** Val Gardena for the anniversary
(also old). Both live on the coast and in Venice now.

### The four-night Dolomites squeeze — a schedule constraint, not a money one

4 nights = **three full days: Oct 11, 12, 13.** Oct 10 is a travel afternoon (boat + car +
drive) and Oct 14 is the drive to Malpensa. Oct 12 is locked to Grey's birthday, which leaves
Oct 11 and Oct 13 for Kronplatz (Keir) and Jude's rocks/minerals day — so **Alpe di Siusi has
no slot** unless it squeezes into the Oct 10 arrival afternoon. Budget the activities line for
three big days in the mountains, not five. Lift dates are **confirmed fine**: Seceda and Mont
Sëuc run to **2 Nov**, Kronplatz bike park to **8 Nov**. (Only the Fermeda chairlift, closing
Sep 20, is out of reach.) The old "confirm the lift dates" warnings are resolved.

## Reconciliation — where the pages disagree

`budget.html` is the low/avg/high **model**; `costs.html` + `costs-data.js` are the **running
ledger**. They are built differently and do not have to match, but here is where they part
company. **None of these are silently resolved above.**

1. **`/costs` counts a second flight line that `/budget` never mentions.** The ledger carries
   **Avianca SJO⇄IAD positioning, Sep 9 – Nov 17, ref AABDA8, $1,870.74, booked** alongside the
   $5,346 Icelandair. Total air committed is therefore **$7,216.74**, not $5,346 — but *all* of
   it sits outside this ground budget. Don't let the $5,346 headline make you forget the
   positioning flights exist.
2. **The two pages measure different things.** `/costs` defaults project **≈ $24,850 all-in**
   against a **$28,000** budget target (89% used, ~$3,150 left, ~$731/day, ~$122/pp/day).
   Strip the $7,217 of air and the ledger's **ground** figure is **≈ $17,633** — which lands
   between this model's **$16,160 low** and **$20,150 average**, nearer the low. The two are
   compatible; `/costs` is simply running a leaner day-to-day than the model's average.
3. **`costs-data.js`: the car line is now correct, the rail line is still stale.**
   - `tr-car` = **$717, status `booked`** — "Rental car · Budget · ref 02391839US2 · VCE Oct 10
     12:00 → MXP Oct 15 12:00 (5d)". ✅ Real, from `public/costs.csv` via
     `tools/build-costs.mjs`. Note the ledger row is the **rental only** — the **~$185** of fuel
     and tolls is *not* in it, so the ledger understates the car leg by that much.
   - `tr-intercity` = **$771** labelled "**6** intercity rail legs (Aug-2026 pull)". $771 =
     €714 × 1.08, i.e. it still contains the dead **€152 Venice → Bolzano** leg. The 5 legs
     that remain are **€561 ≈ $606**. Still overstated by ~$165.
   - Net: $771 + $717 = **$1,488** in the ledger vs. a corrected $606 + $902 = **$1,508**. Close
     enough at the total; the rail line on its own is still wrong.
4. **`/costs` misc runs below the model's floor.** The misc slider defaults to $25/day = **$850**
   over 34 days, against a misc/contingency band of **$1,200–2,300** here. The ledger has no
   contingency in it at all. Read the ledger's headline as "if nothing goes wrong."
5. **`/costs` transit is a blended line.** Its slider is "Local transit **& day-trip trains**"
   ($22/day = $748), so the Bologna day-trip may be double-counted against the intercity-rail
   bucket above, which also names it. Pick one home for it before comparing the two pages.
6. **The site has now absorbed the booked car on the pages that matter.** `trains.html`,
   `plan.html` and `dolomites.html` all carry **Budget ref 02391839US2, VCE Oct 10 12:00 → MXP
   Oct 15 12:00**, and `costs.csv` / `costs-data.js` carry the **$717 booked**. Still stale:
   `budget.html` (car row says "~5 days from Bolzano", rail row says "7 legs", intro says "the 7
   intercity trains"). `housing.html` and several pages still name the last night an **"MXP
   airport hotel"** — that location is **being reconsidered** now that we hold the car overnight,
   so read it as "near Malpensa, TBD."
7. **Venice lodging: $1,800 in the ledger vs. €1,960 ≈ $2,117 in the housing model.** The
   housing page's own average is ~$300 higher than the placeholder. Assume the higher number.

## Next moves (~3 weeks out — Aug 2026)

1. **Book the 5 surviving rail legs.** The Frecce (Milan→Turin, Florence→Rome, Rome→Venice)
   are dynamic-priced like flights and the €561 figure is a *cheapest-advance* pull that decays
   daily. Split the six into **two Offerta Famiglia bookings**, each carrying one of Grey or
   Keir, with passenger ages set.
2. ~~Book the car~~ **DONE ✓ — booked at $717.** Budget, ref **02391839US2**, +1 866-671-7282;
   7-seat automatic (Peugeot 5008 or similar), **VCE Sat Oct 10 12:00 → MXP Terminal 1 Thu Oct 15
   12:00**, 5 days, unlimited mileage, CDW + theft, free cancellation. **Verify the $717 against
   the actual Budget charge** when it posts, and budget **~$185** on top for fuel and tolls.
   What's left in its place: 🔴 **two International Driving Permits** (Dan + Kei, ~$20 each at
   AAA) — legally required in Italy on a US licence and impossible to obtain once abroad.
3. **Book the Alilaguna Lido → Marco Polo boat** for the morning of Oct 10, and check the
   luggage allowance for six people's carry-ons.
4. **Close out the three open lodging estimates** — Venice/Lido (budget ~$2,100, not $1,800),
   the Val Gardena chalet, and **the last night near Malpensa (2 rooms, location TBD — airport
   hotel, or a lake town within ~1h; we have the car, so both are on the table)**. Alpine
   inventory for six thins out fast.
5. **Treat $18–26K as the in-country target** — flights ($5,346 Icelandair + $1,870.74 Avianca
   positioning) are already paid and don't count against it. Aim for the ~$20K average; the
   painless levers pull it toward $16–18K.
6. **Dan's PTO on the car leg:** Wed Oct 14 (driving to the Malpensa area through the
   16:00–23:00 window) and Thu Oct 15 (car back at noon, then flying) both need to be taken. Mon Oct 12 is blocked for Grey's birthday. Tue Oct 13
   is the only normal work evening — keep that day's plan close to base.

See also: [Housing](public/housing.html) · [Trains](public/trains.html) ·
[Celebrations](public/celebrations.html) · [Running total](public/costs.html) ·
live [Budget page](public/budget.html) · [Canonical facts, 21 Aug 2026](DECISIONS-2026-08-21.md).
