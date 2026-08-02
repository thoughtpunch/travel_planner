// The 2026 family loop — LOCKED. Flights booked (Icelandair BWI⇄MXP, Sep 11 arr / Oct 15 dep).
// Milan back to Milan: a rail arc down the spine to Rome, then up the east/north — Bologna,
// Venice, the Dolomites — and out of Malpensa. Family of six, carless except the Dolomites.
// Coordinates are real lat/lng so the map places cities truthfully.
// Each stop links to its own page (in /public) with a Top 10 + full things-to-do.

export const STOPS = [
  {
    n: 1, key: 'milan', name: 'Milan', sub: 'Arrival', color: '#55606E', page: '/milan',
    lat: 45.4642, lng: 9.1900,
    dates: 'Sep 11–13', nights: 2,
    note: 'Land MXP 9:55pm Fri. Duomo rooftop, The Last Supper, Navigli, San Bernardino alle Ossa, Milanese food.',
  },
  {
    n: 2, key: 'como', name: 'Lake Como', sub: 'Ferries + funicular', color: '#2C7A8C', page: '/como',
    lat: 45.8081, lng: 9.0852,
    dates: 'Sep 13–16', nights: 3,
    note: 'Bellagio–Varenna ferry day, Brunate funicular, Como lakefront, villa views, optional Orrido di Bellano.',
  },
  {
    n: 3, key: 'cinqueterre', name: 'Cinque Terre', sub: 'Ligurian coast', color: '#C85A2B', page: '/cinqueterre',
    lat: 44.1263, lng: 9.6841,
    dates: 'Sep 16–18', nights: 2,
    note: 'Manarola, Vernazza, Monterosso; the coastal train and boat; focaccia and pesto. Based Levanto/La Spezia.',
  },
  {
    n: 4, key: 'florence', name: 'Florence', sub: 'Work base · Rhys turns 18', color: '#9C6B2E', page: '/florence',
    lat: 43.7696, lng: 11.2558,
    dates: 'Sep 18–25', nights: 7,
    note: "Rhys's 18th (Sep 18) + splurge pasta dinner. Duomo climb, Stibbert armor, Galileo/HZERO, artisan workshop, Lucca/Pisa day.",
  },
  {
    n: 5, key: 'rome', name: 'Rome', sub: 'Work base', color: '#C4531A', page: '/rome',
    lat: 41.9028, lng: 12.4964,
    dates: 'Sep 25 – Oct 2', nights: 7,
    note: 'Colosseum + Forum, Vatican, pizza class, Baths of Caracalla, Appian Way, San Clemente, Quartiere Coppedè.',
  },
  {
    n: 6, key: 'bologna', name: 'Bologna', sub: 'Food weekend', color: '#D4920A', page: '/bologna',
    lat: 44.4949, lng: 11.3426,
    dates: 'Oct 2–4', nights: 2,
    note: 'Pasta class, Quadrilatero food crawl, porticoes, Palazzo Poggi oddities, tortellini + tagliatelle feast.',
  },
  {
    n: 7, key: 'venice', name: 'Venice / Lido', sub: 'MuMu · lagoon', color: '#1B6B8A', page: '/venice',
    lat: 45.4283, lng: 12.3686,
    dates: 'Oct 4–9', nights: 5,
    note: 'Aunt Muriel (MuMu) visit; Grand Canal, Doge’s Palace, Murano glass, San Michele, Libreria Acqua Alta, lagoon time.',
  },
  {
    n: 8, key: 'dolomites', name: 'Dolomites', sub: 'Anniversary + Grey’s 12th', color: '#4C6B82', page: '/dolomites',
    lat: 46.5477, lng: 11.6706, // Val Gardena — car from Bolzano
    dates: 'Oct 9–14', nights: 5,
    note: 'Anniversary (Oct 9) + Grey turns 12 (Oct 12). Seceda, Alpe di Siusi, Val Gardena villages, scenic drives, Ötzi backup. The one car leg.',
  },
  {
    n: 9, key: 'malpensa', name: 'Malpensa', sub: 'Departure', color: '#8C7B6B', page: '/trains',
    lat: 45.6306, lng: 8.7281,
    dates: 'Oct 14–15', nights: 1,
    note: 'Airport hotel, repack, relaxed final meal. MXP → BWI 4:20pm Thu. Stress-free departure.',
  },
]

// No separate side-dots in the locked plan (Florence is a full stop now).
export const SIDE = []

// Route segments in travel order. mode: 'rail' (train/road) or 'sea' (ferry). No sea legs this year.
export const LEGS = [
  { from: 'milan', to: 'como', mode: 'rail', label: 'Milano Centrale → Como S. Giovanni · ~40 min' },
  { from: 'como', to: 'cinqueterre', mode: 'rail', label: 'Como → Milan → Levanto/La Spezia · ~3h' },
  { from: 'cinqueterre', to: 'florence', mode: 'rail', label: 'La Spezia → Firenze S.M.N. · ~2h30' },
  { from: 'florence', to: 'rome', mode: 'rail', label: 'Frecciarossa · ~1h35' },
  { from: 'rome', to: 'bologna', mode: 'rail', label: 'Frecciarossa · ~2h05' },
  { from: 'bologna', to: 'venice', mode: 'rail', label: 'Frecciarossa → Venezia S. Lucia · ~1h30, vaporetto to Lido' },
  { from: 'venice', to: 'dolomites', mode: 'rail', label: 'Train Venezia → Bolzano · ~3h15, collect rental car' },
  { from: 'dolomites', to: 'malpensa', mode: 'rail', label: 'Return car Bolzano; train → Milano/Malpensa · ~4h' },
]

export const TOTAL_NIGHTS = STOPS.reduce((s, x) => s + x.nights, 0)
