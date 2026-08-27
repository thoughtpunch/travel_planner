// The 2026 family loop — LOCKED. Flights booked (Icelandair BWI⇄MXP, Sep 11 arr / Oct 15 dep).
// Milan back to Milan: a rail arc — Turin and the Ligurian coast, down the spine to Florence
// and Rome, then up through Venice and the Dolomites and out of Malpensa. Family of six,
// carless except the Dolomites.
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
    n: 2, key: 'turin', name: 'Turin', sub: 'Café-and-arcade city · PTO', color: '#2C7A8C', page: '/turin',
    lat: 45.0703, lng: 7.6869,
    dates: 'Sep 13–15', nights: 2,
    note: 'Sacra di San Michele abbey-fortress, Mole Antonelliana + Cinema Museum, Museo Egizio; birthplace of aperitivo, gianduiotto, bicerin.',
  },
  {
    n: 3, key: 'cinqueterre', name: 'Ligurian Coast', sub: 'Base Chiavari · PTO', color: '#C85A2B', page: '/cinqueterre',
    lat: 44.3167, lng: 9.3247,
    dates: 'Sep 15–19', nights: 4,
    note: "Base Chiavari: Cinque Terre by train, Camogli → San Fruttuoso boat, Genoa submarine on arrival, beach rest day. Rhys's 18th (Sep 18) seafood dinner over the Mediterranean.",
  },
  {
    n: 4, key: 'florence', name: 'Florence', sub: 'Work base', color: '#9C6B2E', page: '/florence',
    lat: 43.7696, lng: 11.2558,
    dates: 'Sep 19–26', nights: 7,
    note: 'Duomo climb, Stibbert armor, Galileo/HZERO, artisan workshop, Lucca/Pisa day, Bologna food day-trip (~37 min Frecciarossa).',
  },
  {
    n: 5, key: 'rome', name: 'Rome', sub: 'Work base', color: '#C4531A', page: '/rome',
    lat: 41.9028, lng: 12.4964,
    dates: 'Sep 26 – Oct 3', nights: 7,
    note: 'Colosseum + Forum, Vatican, pizza class, Baths of Caracalla, Appian Way, San Clemente, Quartiere Coppedè.',
  },
  {
    n: 6, key: 'venice', name: 'Venice / Lido', sub: 'MuMu · anniversary · lagoon', color: '#1B6B8A', page: '/venice',
    lat: 45.4408, lng: 12.3155,
    dates: 'Oct 3–10', nights: 7,
    note: 'Aunt Muriel (MuMu) on the Lido; anniversary (Oct 9) dinner on the canals; Grand Canal, Doge’s Palace, Murano glass, San Michele, Libreria Acqua Alta, Padua day-trip.',
  },
  {
    n: 7, key: 'dolomites', name: 'Dolomites', sub: 'Keir’s bike day · Grey’s 12th', color: '#4C6B82', page: '/dolomites',
    lat: 46.5825, lng: 11.5661, // Funtnatsch Apartment Schlern, Laion (Lajen) — booked 26 Aug 2026
    dates: 'Oct 10–14', nights: 4,
    note: 'Base: Funtnatsch Apartment Schlern, Laion (booked — replaced the Singerhof after it cancelled). Grey turns 12 (Oct 12); Keir’s bike ride is the gentle Ortisei railway trail, ~20 min. Ortisei/Seceda ~20 min, Alpe di Siusi cableway ~35, Ötzi ~45. The one car leg.',
  },
  {
    n: 8, key: 'malpensa', name: 'Malpensa', sub: 'Departure', color: '#8C7B6B', page: '/trains',
    lat: 45.6300, lng: 8.7231,
    dates: 'Oct 14–15', nights: 1,
    note: 'Airport hotel, repack, relaxed final meal. MXP → BWI 4:20pm Thu. Stress-free departure.',
  },
]

// No separate side-dots in the locked plan (Florence is a full stop now).
export const SIDE = []

// Route segments in travel order. mode: 'rail' (train/road) or 'sea' (ferry). No sea legs this year.
export const LEGS = [
  { from: 'milan', to: 'turin', mode: 'rail', label: 'Milano Centrale → Torino P. Nuova · ~1h Frecciarossa' },
  { from: 'turin', to: 'cinqueterre', mode: 'rail', label: 'Torino → Genova → Chiavari · ~2h30, change Genoa' },
  { from: 'cinqueterre', to: 'florence', mode: 'rail', label: 'Chiavari → Firenze S.M.N. · ~2h30' },
  { from: 'florence', to: 'rome', mode: 'rail', label: 'Frecciarossa · ~1h35' },
  { from: 'rome', to: 'venice', mode: 'rail', label: 'Frecciarossa → Venezia S. Lucia · ~4h, vaporetto to Lido' },
  { from: 'venice', to: 'dolomites', mode: 'rail', label: 'Alilaguna Lido → VCE, collect the 7-seater, drive to Laion · ~350 km, ~3h30' },
  { from: 'dolomites', to: 'malpensa', mode: 'rail', label: 'Drive Laion → MXP via Lake Garda\'s west shore · ~360 km, ~4h30; drop the car noon Oct 15' },
]

export const TOTAL_NIGHTS = STOPS.reduce((s, x) => s + x.nights, 0)
