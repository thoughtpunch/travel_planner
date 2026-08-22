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
    { id:'fl-ice', cat:'Flights', label:'Icelandair BWI⇄Milan · ref AMBVO4', usd:5346, status:'booked' },
    { id:'fl-avianca', cat:'Flights', label:'Avianca SJO⇄IAD positioning · Sep 9–Nov 17 · ref AABDA8', usd:1870.74, status:'booked', url:'https://gestiona.avianca.com/en/customize-your-trip?pnr=AABDA8&lastname=BARRETT' },
    { id:'lo-milan', cat:'Lodging', label:'Milan — San Siro Airbnb · Sep 11–13', usd:465.6, status:'booked', url:'https://www.airbnb.com/rooms/1452221020381596173' },
    { id:'lo-turin', cat:'Lodging', label:'Turin — Centro Airbnb · Sep 13–15', usd:415.71, status:'booked', note:'free cancellation', url:'https://www.airbnb.com/rooms/1040377631489080309' },
    { id:'lo-coast', cat:'Lodging', label:'Ligurian coast — Chiavari · Sep 15–19 (4n)', usd:547.06, status:'booked', note:'€506.54 · Vista sul Carruggio', url:'https://www.booking.com/hotel/it/vista-sul-carruggio-centro-storico-di-chiavari.en-us.html' },
    { id:'lo-florence', cat:'Lodging', label:'Florence · Sep 19–26 (7n, +Grandma)', usd:1937.57, status:'booked', note:'San Frediano Airbnb', url:'https://www.airbnb.com/rooms/1376653584481814317' },
    { id:'lo-rome', cat:'Lodging', label:'Rome · Sep 26–Oct 3 (7n)', usd:1977, status:'booked', note:'Airbnb 28235127', url:'https://www.airbnb.com/rooms/28235127' },
    { id:'lo-venice', cat:'Lodging', label:'Venice / Lido · Oct 3–10 (7n)', usd:1800, status:'estimate' },
    { id:'lo-dolomites', cat:'Lodging', label:'Dolomites — Singerhof, Kastelruth · Oct 10–14 (4n)', usd:1004, status:'booked', note:'Singerhof, St. Valentin 4, Kastelruth (Castelrotto) BZ · Seiser Alm side of the Schlern · was $1,400 est → $396 under', url:'https://www.booking.com/hotel/it/singerhof.html' },
    { id:'lo-malpensa', cat:'Lodging', label:'Malpensa airport hotel · Oct 14–15 (1n)', usd:170, status:'estimate' },
    { id:'tr-intercity', cat:'Trains', label:'5 intercity rail legs · all 6 (Aug-2026 pull)', usd:606, status:'estimate', note:'was 6 legs/$771 — the Venice→Bolzano leg is replaced by the car' },
    { id:'tr-car', cat:'Trains', label:'Rental car · Budget · ref 02391839US2 · VCE Oct 10 12:00 → MXP Oct 15 12:00 (5d)', usd:717, status:'booked', note:'Peugeot 5008 or similar · 7 seats · automatic · unlimited mileage · CDW + theft · free cancellation · Budget +1 866-671-7282 · verify amount against the Budget charge' },
    { id:'tr-carfuel', cat:'Trains', label:'Rental car — fuel + autostrada tolls (5 days incl. the MXP run)', usd:185, status:'estimate', note:'~€170; A22/A4 tolls ~€35–45 on the Malpensa leg' },
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
