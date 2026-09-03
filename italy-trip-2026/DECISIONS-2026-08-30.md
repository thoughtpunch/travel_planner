# Decisions & corrections — 30 Aug 2026

Supersedes the cost/fare numbers in `01-summary.md`, `03-routes-and-transit.md`,
`04-budget.md`, `05-rome.md`, `09-booking.md` and `DECISIONS-2026-08-21.md`.
**As always, `public/*.html` + the generated data files are the source of truth**;
the numbered docs drift. This file records what changed and why.

---

## 1. Booked ≠ paid. The ledger now tracks both.

`public/costs.csv` gained five columns: `Paid USD`, `Paid Date`, `Pay Ref`,
`Pay Status` (`paid|partial|pending|unknown`), `Due Date`.
`tools/build-costs.mjs` prints a cash position on every build.

**Paid: $11,814.82** · **owed with a date: $5,933.29** · **unknown: $717** (the Budget car).

Four funding sources — no single statement shows this trip:
Visa ••8523, Visa ••8341 (Chase Sapphire), Visa ••2966, and PayPal.

| Date | Amount | What | Source |
|---|---|---|---|
| Sep 4 | $560 | 5 train legs (deadline-driven) | — |
| Sep 7 | $1,029 | Funtnatsch, Laion | Visa ••8341 |
| Sep 13 | $2,285.24 | Rome | **PayPal** |
| Sep 18 | $944.05 | Venice balance | Visa ••2966 |
| Oct 9 | $406 | Osteria della Pista | Visa ••8341 |
| Oct 10 | €57.60 | Laion city tax | cash at property |

**Lodging is $9,262.37, not $8,955** — Rome was recorded $308 light
($1,977 → the real scheduled charge of $2,285.24). Every page carrying $8,955 was swept.

No rule predicts pay-now vs payment-plan: Milan had free cancellation and was charged
instantly; Turin was equally flexible and took nothing until paid early on 29 Aug.

## 2. Trains — book as TWO bookings, not one. Saves €304.

Trenitalia's family offers **cap at 5 passengers**, so a party of six sees none of them.
Verified against the live booking API on 30 Aug: Rome→Venice on the same 09:35 direct
Frecciarossa is **€335.40 as six adults, €203.80 split 4+2**.

- **Booking A** — 2 adults + Grey + Keir → FrecciaFAMILY / BIMBI GRATIS (**under-15s FREE**, adults 50% off Base)
- **Booking B** — Rhys + Jude → FrecciaYOUNG (both under 30; needs a free CartaFreccia signup)

**All five legs: €483 instead of €788.** Seat selection is free on family fares and paid
on Super Economy, so six adjacent seats cost nothing.

**Deadlines** — Chiavari→Florence **Sep 4** · Turin→Chiavari and Florence→Rome **Sep 11** ·
Rome→Venice **Sep 18** · Milan→Turin window already closed, use **FrecciaDAYS €71.40**.

**Carta Verde no longer exists** — withdrawn 1 April 2026.

**⚠️ Milan→Turin leaves from PORTA GARIBALDI, not Centrale.** On Sun Sep 13 Centrale has
zero direct departures 08:45–noon; Garibaldi has six. M5 runs there direct from San Siro.
The old `UB+FR` results were the engine bussing you Centrale→Garibaldi.

## 3. Activities — every one of the 326 is priced for the party of six.

`public/adventure-costs.js` (generated) holds researched 2026 prices; `party-cost.js`
normalises the free-text `k` field for the rest. Both collapse to ONE whole-euro
midpoint so the column sums and averages.

**Dan's rule (30 Aug): free / cultural / nature / low-cost, with 2–3 real splurges for
the whole trip.** He reviewed every activity over $200 by hand and kept eight.
`public/shortlist.js` is that list and is the ONLY exception to the $200 cap —
being a ★must-do no longer earns a pass. 82 activities are hidden; 244 remain, 59 free.

**The shortlist — €2,473 / $2,869:**
Genoa submarine €94 · Cinque Terre sea-kayak €300 · Florencetown pizza+gelato €354 ·
Gladiator school €690 · Murano glassblowing €270 · Seceda €370 · Törggelen €180 ·
Abinea spa €215.

Explicitly rejected as too expensive: AquaFlor perfume (€1,530), Wave Murano furnace
class (€1,225), Scuola del Cuoio leather (€785), Romanelli clay (€625).

## 4. Dolomites — skip the Gardena Card, buy the family ticket.

**Gardena Card: NO.** €596–633 for six, sold only in 3- or 6-**consecutive**-day blocks,
and **validity ends Oct 11** — you arrive Oct 10, so you'd pay for three days and get two.
Singles beat it by €226–430. It also excludes all Alpe di Siusi lifts.

**★ Siusi→Alpe di Siusi has a FAMILY return ticket at €65 for all six** (vs €132 singles).
The two lift systems use different age rules 30 km apart:

| | Junior cutoff | Rhys 18 | Jude 16 |
|---|---|---|---|
| Val Gardena (Seceda, Col Raiser) | **15.99 years** | adult | adult |
| Alpe di Siusi | **born 2008 or later** | **junior** | **junior** |

**Seceda corrected €264 → €370** (4 adults at €74 + 2 juniors at €37).
Bring passports for the family ticket — an 18-year-old will get asked.

**October closures:** Oct 10 (Sat) Prösels shut · **Oct 11 last day for Resciesa**,
Ciampinoi, Forcella Sassolungo, Panorama · Oct 12 (Mon) Trostburg + Klausen museum shut
(so Seceda on Grey's birthday costs nothing in alternatives) · Tue Oct 13 is the only day
both castles open. `/dolomites` said Resciesa ran to November — corrected.

**Both Törggelen festivals are missed** — Gassltörggelen Sep 18–20, Feldthurns Chestnut
Weeks Oct 17. The farm taverns themselves run Oct–Nov, so the shortlist item stands.

**To do:** email the Funtnatsch host — *"do you issue the Südtirol Guest Pass?"* It's free
with participating stays including holiday apartments and gives all six free regional
trains/buses (Ponte Gardena station is at the foot of Laion). It covers **no** lifts.

## 5. City passes — skip all three. Two free Sundays land.

- **Firenze Card** €85pp × 3 payers = €255 vs €147 à la carte. **Skip.**
- **Roma Pass** — cannot break even; best two free entries total €38.50 against €62.90. **Skip.**
- **Venice** — buy the **St Mark's Square ticket (€120)** over the City Pass (€265).
  Junior passes cost €24–35 while reduced entry is €15.
- **DO buy 6 × 7-day ACTV vaporetto passes, €390.** No child rate; everyone pays.
  Break-even is 3.5 round trips and the base is on the Lido.
- **Venice access fee ABOLISHED** from 27 Jul 2026. Nothing to register.

🎯 **Sun Sep 27 — Vatican Museums free** (last Sunday of the month), your first full day in
Rome. Worth ~€90–120. No advance booking, long queues, shortened hours.
🎯 **Sun Oct 4 — Gallerie dell'Accademia Venezia free** (first-Sunday state scheme), plus
Ca' d'Oro, Museo Archeologico, Palazzo Grimani. Venice's *civic* museums opt out.

## 6. Student IDs — don't buy ISIC.

The US issuer limits ISIC to *"full time students at accredited colleges and universities"*,
which excludes Jude at 16 regardless of homeschooling. No homeschool policy exists and no
successful homeschool application is documented.

**Not needed anyway:** Venice's MUVE sells the "studenti 15–25" rate **online with no
document upload** — it operates as an age band. **Buy 4 × Rolling Venice at €6** instead
(ages 6–29, passport only, a named MUVE reduction category).

**Rhys turning 18 on Sep 18 costs real money and nothing fixes it** — from that day he's a
full-price non-EU adult at every Italian state museum; the €2 reduced rate is EU-only.
Anything state-run in Milan or Turin before Sep 18 he still enters free.

## 7. Chase Sapphire

- **$300 annual travel credit** covers passenger trains and car rental agencies — put the
  Trenitalia tickets and the Budget car on it. Check it hasn't already been used this year.
- **No foreign transaction fee** ≈ **$175 saved** on ~$5,850 of ground spend. Primary card in Italy.
- **Don't redeem points.** Chase Travel doesn't sell rail at all; activities redeem at a flat
  1.0¢ and 2026-earned points get no grandfathering. ~10,000 points earned, worth $99–225.
- **Reserve earns 1x on trains; Preferred earns 2x.** Reserve still wins here only via the $300 credit.
- **Rental CDW: UNVERIFIED.** Italy mandates CDW in the base rate, so the card covers the
  excess, not the mandatory portion. Decline only the optional super-CDW upsell —
  and read your own Guide to Benefits before declining anything at the VCE counter.

## 8. Budget

Per-leg snapshots are generated by `tools/build-leg-budgets.mjs` → `public/leg-budgets.js`
and injected into each city page by `public/leg-budget.js`. `/costs` carries the rollup.

**Spend excluding booked lodging: €8,596 lean / €11,063 likely / €14,164 loose**
(≈ $9,971 / $12,833 / $16,430) across 33 nights — about **$385/day** for all six.

Roughly **$7,000 falls in September and $5,500 in October**, before lodging charges.
Add the $4,258 of September lodging and September's real outflow is ~$11,300.

**Biggest levers, in order:** meals out (~$2,900 total — 4/wk instead of 6 saves ~$800) ·
the gladiator school group rate (3+ may discount; ask) · using more of the 59 free options.

## 9. Site & tooling

New: `party-cost.js`, `adventure-costs.js` (gen), `shortlist.js`, `leg-budgets.js` (gen),
`leg-budget.js`, `tools/build-adventure-costs.mjs`, `tools/build-leg-budgets.mjs`.

`/adventures` gained: a party-of-6 cost column, price-band filters, a live roll-up of the
current filter, a **Your picks** total driven by the existing want/booked status, the
shortlist bar, and a card layout below 760px.

**Mobile:** `kids.css` gained a responsive layer (900/720/560/400 breakpoints) shared by 21
pages; `plan.html`'s two unwrapped tables were fixed; all 20 table wrappers now carry
`.table-scroll`. The five "kid pages" (`grey`, `jude`, `keir`, `rhys`, `activities`) are
redirects into `/adventures`, so they need no styling of their own.
