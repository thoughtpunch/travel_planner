// The 2026 family loop — start + end in Rome, all trains + two ferries, no backtracking.
// Coordinates are real lat/lng so the map places cities truthfully.
// Each stop links to its own page (in /public) with a Top 10 + full things-to-do.

export const STOPS = [
  {
    n: 1, key: 'rome-in', name: 'Rome', sub: 'Arrival', color: '#C4531A', page: '/rome',
    lat: 41.9028, lng: 12.4964,
    dates: 'Sep 6 – 11', nights: 5,
    note: 'Land at FCO, decompress. Short opener — the big Rome block is at the end.',
  },
  {
    n: 2, key: 'naples', name: 'Naples', sub: 'Pizza + Salerno', color: '#8C2D1A', page: '/naples',
    lat: 40.8518, lng: 14.2681,
    dates: 'Sep 11 – 21', nights: 10,
    note: "Neapolitan pizza, Vesuvius, Pompeii, Salerno beaches. Rhys's 18th lands here (Sep 18).",
  },
  {
    n: 3, key: 'sicily', name: 'Sicily', sub: 'Palermo + island', color: '#5A7A5C', page: '/sicily',
    lat: 38.1157, lng: 13.3615,
    dates: 'Sep 21 – 28', nights: 7,
    note: 'Overnight ferry from Naples. Etna, Greek temples, mosaics; optional Malta hop.',
  },
  {
    n: 4, key: 'bologna', name: 'Bologna', sub: 'Hub · Motor Valley · Florence', color: '#D4920A', page: '/bologna',
    lat: 44.4949, lng: 11.3426,
    dates: 'Sep 28 – Oct 19', nights: 21,
    note: 'Cheap rail hub. Florence 2–3 nights, Ferrari/Lambo/Ducati, Cremona, Ravenna. Grandma Oct 1–14, Grey turns 12 on Oct 12.',
  },
  {
    n: 5, key: 'dolomites', name: 'Dolomites', sub: 'Bolzano base · long weekend', color: '#1B6B8A', page: '/bolzano',
    lat: 46.4983, lng: 11.3548, // Bolzano — the right base in late Oct (Cortina shuts by ~Oct 18)
    dates: 'Oct 19 – 22', nights: 3,
    note: 'Base in Bolzano (not Cortina): Ötzi the Iceman, Earth Pyramids, frescoed castles, last Seceda/Braies days.',
  },
  {
    n: 6, key: 'venice', name: 'Venice / Lido', sub: 'Family · 2 weeks', color: '#1B6B8A', page: '/venice',
    lat: 45.4283, lng: 12.3686,
    dates: 'Oct 22 – Nov 5', nights: 14,
    note: 'Based on the Lido to see family. Murano glassblowing, St Mark’s mosaics, Doge’s armoury, Burano.',
  },
  {
    n: 7, key: 'croatia', name: 'Croatia', sub: 'Split · Kotor · Dubrovnik', color: '#7A4FB5', page: '/croatia',
    lat: 43.5081, lng: 16.4402,
    dates: 'Nov 5 – 12', nights: 7,
    note: 'No Nov ferry from Venice — enter via Ancona→Split. Klis fortress, Dubrovnik walls, Kotor (Montenegro).',
  },
  {
    n: 8, key: 'rome-out', name: 'Rome', sub: 'Departure', color: '#C4531A', page: '/rome',
    lat: 41.835, lng: 12.72, // nudged SE of the arrival pin so both Rome stops show
    dates: 'Nov 12 – 20', nights: 8,
    note: 'Fly Dubrovnik→Rome. The real Rome deep-dive, then fly home Nov 20.',
  },
]

// Florence gets its own dot (2–3 nights off the Bologna hub) but isn't a separate leg.
export const SIDE = [
  { key: 'florence', name: 'Florence', sub: '2–3 nights from Bologna', lat: 43.7696, lng: 11.2558, color: '#D4920A' },
]

// Route segments in travel order. mode: 'rail' (train/road) or 'sea' (ferry/flight over water).
export const LEGS = [
  { from: 'rome-in', to: 'naples', mode: 'rail', label: 'Frecciarossa · ~1h10' },
  { from: 'naples', to: 'sicily', mode: 'sea', label: 'Overnight ferry to Palermo' },
  { from: 'sicily', to: 'bologna', mode: 'rail', label: 'Messina ferry + long train day' },
  { from: 'bologna', to: 'dolomites', mode: 'rail', label: 'Train to Bolzano · ~2h30' },
  { from: 'dolomites', to: 'venice', mode: 'rail', label: 'Train · ~2h45' },
  { from: 'venice', to: 'croatia', mode: 'sea', label: 'Train to Ancona → overnight ferry to Split (no Nov Venice ferry)' },
  { from: 'croatia', to: 'rome-out', mode: 'sea', label: 'Fly Dubrovnik → Rome (or ferry + train)' },
]

export const TOTAL_NIGHTS = STOPS.reduce((s, x) => s + x.nights, 0)
