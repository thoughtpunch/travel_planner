/* ============================================================================
 * costs-data.js — the trip cost model (defaults)
 * ----------------------------------------------------------------------------
 * Plain, hand-editable defaults for the /costs running-total tracker.
 * The page (costs.html) reads this, then layers ANY edits the user makes in the
 * browser on top (saved to localStorage under "tripCostsV1"), so booked amounts
 * and slider positions persist across visits with no server.
 *
 * To bake a number in permanently (so it's the default even after a Reset),
 * change it HERE and redeploy. All amounts are USD. EUR estimates were
 * pre-converted at ~1.08 (noted inline).
 * ==========================================================================*/
window.TRIP_COSTS = {
  budgetUSD: 28000,   // EDIT — Dan's all-in target. Also editable live on the page.
  days: 34,           // Sep 11 → Oct 15, nights on the ground
  people: 6,

  // ── Committed + planned line items (the ledger) ──────────────────────────
  // status: 'booked' = paid/reserved, real number.  'estimate' = placeholder.
  // usd:null = booked but amount not entered yet (shows an input, excluded til set).
  fixed: [
    { id:'fl-ice', cat:'Flights', label:'Icelandair BWI⇄Milan · ref AMBVO4', usd:5346, status:'booked', pay:'paid', paidUsd:5346, payRef:'Icelandair ref AMBVO4' },
    { id:'fl-avianca', cat:'Flights', label:'Avianca SJO⇄IAD positioning · Sep 9–Nov 17 · ref AABDA8', usd:1870.74, status:'booked', url:'https://gestiona.avianca.com/en/customize-your-trip?pnr=AABDA8&lastname=BARRETT', pay:'paid', paidUsd:1870.74, payRef:'Avianca ref AABDA8' },
    { id:'lo-milan', cat:'Lodging', label:'Milan — San Siro Airbnb · Sep 11–13', usd:465.6, status:'booked', note:'Host Fabio Mulà · conf HMZTC88P45 · $161.40 × 2 nts = $322.79, −$32.86 discount, $44.25 service fee, $131.42 taxes (tassa di soggiorno INCLUDED) · free cancellation to 3 PM Sep 10', url:'https://www.airbnb.com/rooms/1452221020381596173', pay:'paid', paidUsd:465.6, paidDate:'2026-08-13', payRef:'Airbnb receipt RCPNR5ABW5 · Visa ••8523' },
    { id:'lo-turin', cat:'Lodging', label:'Turin — Centro Airbnb · Sep 13–15', usd:415.71, status:'booked', note:'\\Mole\\ House · 2BR/1bath, 6 adults · reservation HMMSR2JEC5 · free cancellation · was an Airbnb payment plan due Sep 4 on Visa ••8523 — PAID EARLY 29 Aug on the Chase Sapphire instead, balance now $0', url:'https://www.airbnb.com/rooms/1040377631489080309', pay:'paid', paidUsd:415.71, paidDate:'2026-08-29', payRef:'Airbnb HMMSR2JEC5 · Visa ••8341 (Chase Sapphire)' },
    { id:'lo-coast', cat:'Lodging', label:'Ligurian coast — Chiavari · Sep 15–19 (4n)', usd:547.06, status:'booked', note:'€506.54 · Vista sul Carruggio', url:'https://www.booking.com/hotel/it/vista-sul-carruggio-centro-storico-di-chiavari.en-us.html', pay:'paid', paidUsd:547.06, paidDate:'2026-08-13', payRef:'Booking.com · Visa ••8341 · €506.54' },
    { id:'lo-florence', cat:'Lodging', label:'Florence · Sep 19–26 (7n, +Grandma)', usd:1937.57, status:'booked', note:'San Frediano Airbnb · host Edoardo Matucci · conf HMMQEFQS2H · $259.44 × 7 nts = $1,816.06, −$170.04 weekly discount, $291.55 taxes (tassa di soggiorno INCLUDED) · NON-REFUNDABLE', url:'https://www.airbnb.com/rooms/1376653584481814317', pay:'paid', paidUsd:1937.57, paidDate:'2026-08-15', payRef:'Airbnb receipt RCD3PQCPJ2 · Visa ••8523' },
    { id:'lo-rome', cat:'Lodging', label:'Rome · Sep 26–Oct 3 (7n)', usd:2285.24, status:'booked', note:'Domus Flavii Re di Roma · Airbnb 28235127 · reservation HMHZNB9MW3 · Airbnb payment PLAN — nothing taken at booking, full amount charges Sep 13 · AMOUNT CORRECTED: ledger said $1,977, the actual scheduled charge is $2,285.24 (+$308.24) · paid via PayPal, NOT the Visa ••8523 used for the other Airbnbs', url:'https://www.airbnb.com/rooms/28235127', pay:'pending', paidUsd:0, payRef:'Airbnb HMHZNB9MW3 · PayPal k••••a@gmail.com', dueDate:'2026-09-13' },
    { id:'lo-venice', cat:'Lodging', label:'Venice / Lido · Oct 3–10 (7n)', usd:2176.19, status:'booked', note:'Appartamento alle terrazze · Lido di Venezia — next door to MuMu, which is the whole point of the leg · reservation HMQTHRTN3R · SPLIT PAYMENT: $1,232.14 taken Aug 22, balance $944.05 charges Sep 18 · was $1,800 est → $376 over', url:'https://www.airbnb.com/rooms/1151356839669861774', pay:'partial', paidUsd:1232.14, paidDate:'2026-08-22', payRef:'Airbnb HMQTHRTN3R · Visa ••2966 · balance $944.05 due Sep 18', dueDate:'2026-09-18' },
    { id:'lo-dolomites', cat:'Lodging', label:'Dolomites — Funtnatsch Apartment Schlern, Laion · Oct 10–14 (4n)', usd:1029, status:'booked', note:'Funtnatsch Apartment Schlern, 39040 Laion (Lajen) BZ · conf 5740340654, PIN 7729 · €883.44 · 90 m², 2BR + sofa bed = 6, 1 bath, free private parking · FREE CANCELLATION TO SEP 10 · replaced the Singerhof after the property cancelled 2026-08-26 · €0 paid so far — Booking.com shows the full €883.44 SCHEDULED, not captured', url:'https://www.booking.com/hotel/it/funtnatsch-apartment-schlern.html', pay:'pending', paidUsd:0, payRef:'Booking.com · Visa ••8341 (Chase Sapphire) · conf 5740340654 · €883.44', dueDate:'2026-09-07' },
    { id:'lo-dolomites-tax', cat:'Lodging', label:'Dolomites — Laion city tax (collected by the property)', usd:72, status:'booked', note:'€57.60 · US$3 per person per night × 6 × 4 nights · NOT part of the €883.44 card charge — payable at the property. NOTE: the Airbnb stays bake tassa di soggiorno into their totals (Milan showed $131.42 of tax inside its $465.60), so this separate-tax problem is a Booking.com one — check Chiavari and Osteria della Pista for the same', url:'https://www.booking.com/hotel/it/funtnatsch-apartment-schlern.html', pay:'pending', paidUsd:0, payRef:'pay at property', dueDate:'2026-10-10' },
    { id:'lo-malpensa', cat:'Lodging', label:'Malpensa — Osteria della Pista, Casorate Sempione · Oct 14–15 (1n)', usd:406, status:'booked', note:'Via Verbano 1, 21011 Casorate Sempione VA · 9 min from MXP, free airport shuttle, restaurant on site · was $170 est → $236 over', url:'https://www.booking.com/hotel/it/osteria-della-pista.html', pay:'pending', paidUsd:0, payRef:'Booking.com · Visa ••8341 (Chase Sapphire) · €348', dueDate:'2026-10-09' },
    { id:'tr-intercity', cat:'Trains', label:'5 intercity rail legs · SPLIT 4+2 booking', usd:560, status:'estimate', note:'€483 via the family-fare split (Booking A: 2 adults + Grey + Keir on FrecciaFAMILY/BIMBI GRATIS, under-15s FREE; Booking B: Rhys + Jude on FrecciaYOUNG). Was €788 booking all six as adults — the offers cap at 5 pax so a party of 6 sees none of them. DEADLINES: Chiavari→Florence Sep 4, Turin→Chiavari + Florence→Rome Sep 11, Rome→Venice Sep 18; Milan→Turin window closed, use FrecciaDAYS €71', pay:'pending', paidUsd:0, dueDate:'2026-09-04' },
    { id:'tr-car', cat:'Trains', label:'Rental car · Budget · ref 02391839US2 · VCE Oct 10 12:00 → MXP Oct 15 12:00 (5d)', usd:717, status:'booked', note:'Peugeot 5008 or similar · 7 seats · automatic · unlimited mileage · CDW + theft · free cancellation · Budget +1 866-671-7282 · free cancellation implies pay-at-counter — VERIFY whether the card has been charged', pay:'unknown', paidUsd:null, payRef:'Budget ref 02391839US2' },
    { id:'tr-carfuel', cat:'Trains', label:'Rental car — fuel + autostrada tolls (5 days incl. the MXP run)', usd:185, status:'estimate', note:'~€170; A22/A4 tolls ~€35–45 on the Malpensa leg', pay:'pending', paidUsd:0 },
    { id:'tr-actv', cat:'Trains', label:'Venice — 6 × 7-day ACTV vaporetto pass', usd:452, status:'estimate', note:'€390 (6 × €65). No child rate and no family discount on ACTV — everyone pays. Break-even is 3.5 round trips and the base is on the Lido, so this beats singles by ~€180', url:'https://www.veneziaunica.it/en/buy-tickets/public-trasport-in-venice', pay:'pending', paidUsd:0 },
  ],

  // ── The daily model (sliders) ────────────────────────────────────────────
  // Variable "ground" spend, modeled per-day across all `days`, recomputed live.
  sliders: {
    dinnersOutPerWeek: { label:'Dinners OUT per week', value:3, min:0, max:7, step:1, unit:'/wk' },
    dailyFoodBase:     { label:'Daily food base (breakfast · lunch · snacks, all 6)', value:55, min:20, max:120, step:5, unit:'$/day' },
    activitiesPerDay:  { label:'Activities & entries', value:40, min:0, max:150, step:5, unit:'$/day' },
    transitPerDay:     { label:'Local transit & day-trip trains', value:22, min:0, max:60, step:2, unit:'$/day' },
    miscPerDay:        { label:'Misc (SIMs, laundry, sundries, gifts)', value:25, min:0, max:60, step:5, unit:'$/day' },
  },

  // Cost assumptions behind the dinner slider (for all 6 people):
  dinnerModel: { restaurantDinner6: 130, cookedDinner6: 40 },
};
