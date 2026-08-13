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
    { id:'fl-ice',      cat:'Flights', label:'Icelandair BWI⇄Milan · ref AMBVO4', usd:5346,    status:'booked' },
    { id:'fl-avianca',  cat:'Flights', label:'Avianca SJO⇄IAD positioning · ref AABDA8', usd:1870.74, status:'booked' },

    { id:'lo-milan',    cat:'Lodging', label:'Milan — San Siro Airbnb · Sep 11–13', usd:465.60, status:'booked' },
    { id:'lo-turin',    cat:'Lodging', label:'Turin — Centro Airbnb · Sep 13–15',    usd:415.71, status:'booked', note:'free cancellation' },
    { id:'lo-coast',    cat:'Lodging', label:'Ligurian coast — Chiavari · Sep 15–19 (4n)', usd:547.06, status:'booked', note:'€506.54 · Vista sul Carruggio' }, // €506.54
    { id:'lo-florence', cat:'Lodging', label:'Florence · Sep 19–26 (7n)',            usd:1700,  status:'estimate' },
    { id:'lo-rome',     cat:'Lodging', label:'Rome · Sep 26–Oct 3 (7n)',             usd:1600,  status:'estimate' },
    { id:'lo-venice',   cat:'Lodging', label:'Venice / Lido · Oct 3–10 (7n)',        usd:1800,  status:'estimate' },
    { id:'lo-dolomites',cat:'Lodging', label:'Dolomites / Val Gardena chalet · Oct 10–14 (4n)', usd:1400, status:'estimate' }, // ~€1300
    { id:'lo-malpensa', cat:'Lodging', label:'Malpensa airport hotel · Oct 14–15 (1n)', usd:170, status:'estimate' },

    { id:'tr-intercity',cat:'Trains',  label:'6 intercity rail legs · all 6 (Aug-2026 pull)', usd:771, status:'estimate' }, // €714
    { id:'tr-car',      cat:'Trains',  label:'Dolomites rental car + fuel/tolls · ~5d', usd:650, status:'estimate' },
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
