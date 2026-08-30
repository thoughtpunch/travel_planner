/* build-leg-budgets.mjs — one source of truth for the per-leg budget snapshots
 * ---------------------------------------------------------------------------
 *   node tools/build-leg-budgets.mjs   →  public/leg-budgets.js
 *
 * Pulls REAL numbers from the files that already hold them:
 *   • lodging      ← public/costs.csv          (actual booked amounts)
 *   • activities   ← adventure-costs.js + shortlist.js  (researched, party-of-6)
 *   • trains       ← the FAMILY-FARE plan below (4+2 split, verified 2026-08-30)
 * and layers a low/avg/high daily model on top for food, transit and incidentals.
 *
 * Rendered by leg-budget.js, which self-injects a card into each city page.
 * EDIT THE DAILY RATES HERE — they are the only hand-tuned numbers left.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const P = f => path.join(ROOT, 'public', f);
const EUR_USD = 1.16;

// ── daily per-day rates for the whole party, in EUR ────────────────────────
// low = cooking most nights, cheap eats · avg = one meal out most days
// high = eating out more, taxis, the odd bad-weather day
const DAILY = {
  groceries: { lo: 35, avg: 45, hi: 58, label: 'Groceries — breakfast in, packed lunches' },
  mealOut:   { lo: 62, avg: 86, hi: 118, label: 'One meal out (~6×/week)' },
  snacks:    { lo: 12, avg: 18, hi: 26, label: 'Coffee, gelato, snacks' },
  misc:      { lo: 22, avg: 35, hi: 50, label: 'SIM, laundry, pharmacy, gifts' },
};

// ── the legs ───────────────────────────────────────────────────────────────
// `page` = the URL pathname the card injects onto. `getHere` = the travel cost
// INTO this leg, already using the 4+2 family-fare split.
const LEGS = [
  { leg:1, page:'/milan',       city:'Milan',            dates:'Sep 11–13',    nights:2, people:6,
    lodgingId:'lo-milan',    getHere:{ eur:52,  note:'Malpensa Express into the city, 6 tickets' },
    transit:{ lo:20, avg:34, hi:50, note:'ATM day tickets / M5 from San Siro' } },
  { leg:2, page:'/turin',       city:'Turin',            dates:'Sep 13–15',    nights:2, people:6,
    lodgingId:'lo-turin',    getHere:{ eur:71,  note:'Milano P. Garibaldi → Torino P. Nuova, FrecciaDAYS all six' },
    transit:{ lo:12, avg:22, hi:36, note:'Centre is walkable from Via San Massimo' } },
  { leg:3, page:'/cinqueterre', city:'Ligurian coast',   dates:'Sep 15–19',    nights:4, people:6,
    lodgingId:'lo-coast',    getHere:{ eur:62,  note:'Torino → Chiavari, direct IC, BIMBI GRATIS + YOUNG split' },
    transit:{ lo:70, avg:110, hi:160, note:'Coast regionali + Cinque Terre hops (Chiavari is outside the card zone)' } },
  { leg:4, page:'/florence',    city:'Florence',         dates:'Sep 19–26',    nights:7, people:7,
    lodgingId:'lo-florence', getHere:{ eur:91,  note:'Chiavari → Firenze SMN, FrecciaFAMILY + Super Economy split' },
    transit:{ lo:25, avg:45, hi:70, note:'Mostly walkable; buses + the Bologna day-trip fare' } },
  { leg:5, page:'/rome',        city:'Rome',             dates:'Sep 26–Oct 3', nights:7, people:6,
    lodgingId:'lo-rome',     getHere:{ eur:88,  note:'Firenze SMN → Roma Termini, FrecciaFAMILY + FrecciaYOUNG' },
    transit:{ lo:50, avg:80, hi:115, note:'Metro A from San Giovanni most days' } },
  { leg:6, page:'/venice',      city:'Venice / Lido',    dates:'Oct 3–10',     nights:7, people:6,
    lodgingId:'lo-venice',   getHere:{ eur:170, note:'Roma Termini → Venezia S. Lucia, FrecciaFAMILY + FrecciaYOUNG' },
    transit:{ lo:342, avg:390, hi:430, note:'6 × 7-day ACTV pass €65 — no child rate, everyone pays' } },
  { leg:7, page:'/dolomites',   city:'Dolomites · Laion', dates:'Oct 10–14',   nights:4, people:6,
    lodgingId:'lo-dolomites', getHere:{ eur:0,  note:'No train — the rental car covers this leg' },
    transit:{ lo:120, avg:160, hi:210, note:'Fuel + A22/A4 tolls for the 5-day rental' } },
];

// ── read the real lodging numbers out of costs.csv ─────────────────────────
function parseCSV(text) {
  const rows = []; let row = [], field = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i+1] === '"') { field += '"'; i++; } else q = false; } else field += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else if (c !== '\r') field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows.filter(r => r.some(v => v !== ''));
}
const csv = parseCSV(fs.readFileSync(P('costs.csv'), 'utf8'));
const head = csv.shift().map(h => h.trim().toLowerCase());
const ci = n => head.indexOf(n);
const LODGING = {}, PAYSTATE = {};
for (const r of csv) {
  LODGING[r[ci('id')].trim()] = Number(r[ci('amount usd')].replace(/[$,]/g, '')) || 0;
  PAYSTATE[r[ci('id')].trim()] = (r[ci('pay status')] || 'unknown').trim();
}

// ── activities per leg, from the researched party-of-6 costs ───────────────
globalThis.window = {};
for (const f of ['adventures-data.js', 'party-cost.js', 'adventure-costs.js', 'shortlist.js'])
  new Function(fs.readFileSync(P(f), 'utf8')).call(globalThis);
const ADV = globalThis.window.TRIP_ADVENTURES;
const pc = globalThis.window.partyCost;
const AC = globalThis.window.ADVENTURE_COSTS;
const KEEP = new Set(globalThis.window.TRIP_SHORTLIST);
const slug = (l, n) => l + '-' + String(n).toLowerCase().normalize('NFKD')
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
const costOf = it => {
  const o = AC[slug(it.leg, it.n)];
  if (o) return Math.round((o.lo + o.hi) / 2);
  const p = pc(it.k, it.leg);
  return p ? Math.round((p.lo + p.hi) / 2) : null;
};

const CAP = 172;   // ≈$200 — Dan's cull line
function activitiesFor(leg, nights) {
  const shortlist = ADV.filter(it => it.leg === leg && KEEP.has(slug(it.leg, it.n)))
    .map(it => ({ n: it.n, eur: costOf(it) }));
  const fixed = shortlist.reduce((t, s) => t + s.eur, 0);
  // everyday pool: paid, under the cap, not already a shortlist pick
  const pool = ADV.filter(it => it.leg === leg && !KEEP.has(slug(it.leg, it.n)))
    .map(costOf).filter(v => v !== null && v > 0 && v <= CAP).sort((a, b) => a - b);
  const med = pool.length ? pool[Math.floor(pool.length / 2)] : 0;
  // roughly one outing per day, but many days are free or rest days
  const paidDays = { lo: Math.max(0, Math.round(nights * 0.25)),
                     avg: Math.max(0, Math.round(nights * 0.5)),
                     hi:  Math.max(0, Math.round(nights * 0.8)) };
  return {
    shortlist, fixed, median: med,
    lo: fixed + paidDays.lo * med,
    avg: fixed + paidDays.avg * med,
    hi: fixed + paidDays.hi * med,
  };
}

// ── assemble ───────────────────────────────────────────────────────────────
const out = LEGS.map(L => {
  const act = activitiesFor(L.leg, L.nights);
  const day = k => ({ lo: DAILY[k].lo * L.nights, avg: DAILY[k].avg * L.nights, hi: DAILY[k].hi * L.nights });
  const g = day('groceries'), m = day('mealOut'), s = day('snacks'), x = day('misc');
  const lodgingUsd = LODGING[L.lodgingId] || 0;
  const lodgingEur = Math.round(lodgingUsd / EUR_USD);

  const rows = [
    { key:'lodging',    label:'Lodging',                 lo:lodgingEur, avg:lodgingEur, hi:lodgingEur, fixed:true,
      badge: (PAYSTATE[L.lodgingId] === 'paid' ? 'paid' : PAYSTATE[L.lodgingId] === 'partial' ? 'part-paid' : 'booked'),
      note:'actual booked amount' },
    { key:'getHere',    label:'Getting here',            lo:L.getHere.eur, avg:L.getHere.eur, hi:L.getHere.eur, fixed:true,
      badge: L.getHere.eur ? 'to book' : null, note:L.getHere.note },
    { key:'groceries',  label:DAILY.groceries.label,     ...g },
    { key:'mealOut',    label:DAILY.mealOut.label,       ...m },
    { key:'snacks',     label:DAILY.snacks.label,        ...s },
    { key:'activities', label:'Activities & entries',    lo:act.lo, avg:act.avg, hi:act.hi,
      note: act.shortlist.length ? act.shortlist.length + ' shortlisted + ~€' + act.median + ' typical outing' : '~€' + act.median + ' typical outing' },
    { key:'transit',    label:'Local transport',         lo:L.transit.lo, avg:L.transit.avg, hi:L.transit.hi, note:L.transit.note },
    { key:'misc',       label:DAILY.misc.label,          ...x },
  ];
  const tot = k => rows.reduce((t, r) => t + r[k], 0);
  const spend = k => rows.filter(r => r.key !== 'lodging').reduce((t, r) => t + r[k], 0);
  return {
    leg:L.leg, page:L.page, city:L.city, dates:L.dates, nights:L.nights, people:L.people,
    rows,
    total:  { lo:tot('lo'),   avg:tot('avg'),   hi:tot('hi') },
    spend:  { lo:spend('lo'), avg:spend('avg'), hi:spend('hi') },   // excludes booked lodging
    perDay: { lo:Math.round(spend('lo')/L.nights), avg:Math.round(spend('avg')/L.nights), hi:Math.round(spend('hi')/L.nights) },
    shortlist: act.shortlist,
  };
});

const js = `/* ============================================================================
 * leg-budgets.js — GENERATED by tools/build-leg-budgets.mjs. Do not edit by hand.
 * Per-leg budget snapshots: low / average / high, in EUR, for the whole party.
 * Lodging is the real booked amount; everything else is a modelled band.
 * ==========================================================================*/
window.EUR_USD = ${EUR_USD};
window.LEG_BUDGETS = ${JSON.stringify(out, null, 1)};
`;
fs.writeFileSync(P('leg-budgets.js'), js);

// ── report ─────────────────────────────────────────────────────────────────
const f = n => String(Math.round(n)).padStart(6);
console.log('leg-budgets.js written\n');
console.log('leg city                nts   SPEND (excl. lodging)      per day        lodging');
console.log('                              low    avg    high      low  avg  high');
let T = { lo:0, avg:0, hi:0 }, L2 = 0;
for (const b of out) {
  T.lo += b.spend.lo; T.avg += b.spend.avg; T.hi += b.spend.hi;
  L2 += b.rows[0].avg;
  console.log(' ' + b.leg + '  ' + b.city.padEnd(20) + String(b.nights).padStart(3) +
    f(b.spend.lo) + f(b.spend.avg) + f(b.spend.hi) + '   ' +
    String(b.perDay.lo).padStart(4) + String(b.perDay.avg).padStart(5) + String(b.perDay.hi).padStart(6) +
    f(b.rows[0].avg));
}
console.log('    ' + ' '.repeat(20) + '    ------ ------ ------');
console.log('    TOTAL SPEND (excl lodging)' + f(T.lo) + f(T.avg) + f(T.hi) + '  EUR');
console.log('    ' + ' '.repeat(22) + f(T.lo*EUR_USD) + f(T.avg*EUR_USD) + f(T.hi*EUR_USD) + '  USD');
console.log('    lodging already booked: €' + Math.round(L2) + ' ($' + Math.round(L2*EUR_USD) + ')');
