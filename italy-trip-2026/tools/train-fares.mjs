#!/usr/bin/env node
/*
 * train-fares.mjs — cheapest advance Trenitalia fares per departure
 * ==================================================================
 *
 * Zero-dependency Node.js (>=18, uses the built-in global `fetch`) CLI that
 * queries lefrecce.it's live BFF fare API and prints, for each departure,
 * the CHEAPEST bookable advance fare (Super Economy / Economy / Base — the
 * API already surfaces the lowest as `solution.price`).
 *
 * USAGE
 * -----
 *   Single leg:
 *     node train-fares.mjs "Milano Centrale" "Chiavari" 2026-09-13
 *     node train-fares.mjs "Milano Centrale" "Roma Termini" 2026-09-13 6
 *       args: <origin> <destination> <date YYYY-MM-DD> [adults=6]
 *
 *   All family legs (dates/config in the LEGS block below — EDIT ME):
 *     node train-fares.mjs --all-legs
 *
 * WHAT IT PRINTS
 * --------------
 *   - Which station each name resolved to (so a wrong match is obvious).
 *   - A table per query: departure, arrival, duration, train(s)/changes,
 *     and the cheapest total fare for the whole party (+ per-person).
 *   - Rows sorted by price ascending; the overall-cheapest row is marked
 *     "<= CHEAPEST" and the earliest departure is marked "(earliest)".
 *
 * THE DATADOME / BOT-PROTECTION CAVEAT
 * ------------------------------------
 * lefrecce.it sits behind DataDome-class bot protection. In testing
 * (Aug 2026) a PLAIN `fetch` with realistic browser headers WORKED — both
 * the station-lookup GET and the fare-search POST returned HTTP 200 with
 * real JSON. So the default path here is plain HTTP and needs no browser.
 *
 * If DataDome tightens and this starts returning HTTP 403 or an HTML
 * challenge instead of JSON, DO NOT try to defeat DataDome. Instead run the
 * exact same request from inside a real, logged-in lefrecce.it browser tab,
 * where a same-origin fetch sails past the bot wall. The function
 * `buildBrowserSnippet()` at the bottom emits a self-contained snippet you
 * paste into the chrome-devtools MCP `evaluate_script` tool (or DevTools
 * console) on an open www.lefrecce.it tab. See the README section printed by
 * `node train-fares.mjs --browser-help`.
 */

// ---------------------------------------------------------------------------
// EDIT ME — the family's 5 legs (carless family of 6, all Trenitalia).
// Placeholder dates are reasonable defaults; change them as the plan firms up.
// ---------------------------------------------------------------------------
const ADULTS_DEFAULT = 6;
const LEGS = [
  { from: 'Milano Centrale',    to: 'Torino Porta Nuova', date: '2026-09-13' },
  { from: 'Torino Porta Nuova', to: 'Chiavari',           date: '2026-09-15' },
  // NOTE: use "Firenze S. M. Novella" — the API's lookup can't parse "S.M.N."
  { from: 'Chiavari',           to: 'Firenze S. M. Novella', date: '2026-09-19' },
  { from: 'Firenze S. M. Novella', to: 'Roma Termini',    date: '2026-09-26' },
  { from: 'Roma Termini',       to: 'Venezia S. Lucia',   date: '2026-10-03' },
  { from: 'Venezia S. Lucia',   to: 'Bolzano',            date: '2026-10-10' },
];

// ---------------------------------------------------------------------------
// API constants
// ---------------------------------------------------------------------------
const BASE = 'https://www.lefrecce.it/Channels.Website.BFF.WEB/website';
const LOCATIONS_URL = `${BASE}/locations/search`;
const SOLUTIONS_URL = `${BASE}/ticket/solutions`;

const HEADERS = {
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  Accept: 'application/json, text/plain, */*',
  'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
  Origin: 'https://www.lefrecce.it',
  Referer: 'https://www.lefrecce.it/',
  'Content-Type': 'application/json',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Detect a DataDome / bot-wall response so we can print a helpful message. */
function looksBlocked(status, text) {
  if (status === 403 || status === 401) return true;
  const t = (text || '').slice(0, 400).toLowerCase();
  return t.includes('datadome') || t.includes('captcha') || t.startsWith('<!doctype html');
}

class BlockedError extends Error {}

async function apiFetch(url, opts = {}) {
  let res;
  try {
    res = await fetch(url, { ...opts, headers: { ...HEADERS, ...(opts.headers || {}) } });
  } catch (e) {
    throw new Error(`Network error calling ${url}: ${e.message}`);
  }
  const text = await res.text();
  if (looksBlocked(res.status, text)) {
    throw new BlockedError(
      `Bot wall hit (HTTP ${res.status}). The plain-fetch path is being blocked by ` +
      `DataDome. Re-run the request from a real lefrecce.it browser tab — see ` +
      `\`node train-fares.mjs --browser-help\`.`
    );
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} from ${url}: ${text.slice(0, 200)}`);
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Non-JSON response from ${url}: ${text.slice(0, 200)}`);
  }
}

/** Resolve a station name to a lefrecce location id (top match). */
async function resolveStation(name) {
  const url = `${LOCATIONS_URL}?name=${encodeURIComponent(name)}&limit=10`;
  const list = await apiFetch(url);
  if (!Array.isArray(list) || list.length === 0) {
    throw new Error(`No station matched "${name}".`);
  }
  const top = list[0];
  return { id: top.id, name: top.name, query: name };
}

/** POST the fare search and return the raw solutions array. */
async function searchFares({ departureLocationId, arrivalLocationId, date, adults }) {
  const body = {
    departureLocationId,
    arrivalLocationId,
    departureTime: `${date}T00:00:00.000`, // whole-day search; API returns the day's departures
    adults,
    children: 0,
    criteria: {
      frecceOnly: false,
      regionalOnly: false,
      noChanges: false,
      order: 'DEPARTURE_DATE',
      limit: 20,
      offset: 0,
    },
    advancedSearchRequest: { bestFare: false },
  };
  const json = await apiFetch(SOLUTIONS_URL, { method: 'POST', body: JSON.stringify(body) });
  return json.solutions || [];
}

/** Flatten a raw solution into the fields we print. */
function normalizeSolution(entry, adults) {
  const s = entry.solution || {};
  const price = s.price || {};
  const hasPrice = price.amount != null && !price.hideAmount;
  const trains = (s.trains || []).map((t) => t.acronym || t.trainCategory || '?');
  return {
    dep: s.departureTime,
    arr: s.arrivalTime,
    duration: s.duration || '',
    trains,
    changes: Math.max(0, trains.length - 1),
    amount: hasPrice ? Number(price.amount) : null,
    perPerson: hasPrice ? Number(price.amount) / adults : null,
    currency: price.currency || '€',
    status: s.status || '',
    indicative: !!price.indicative,
  };
}

function hhmm(iso) {
  if (!iso) return '--:--';
  // ISO like 2026-09-13T08:30:00.000+02:00 — take the local wall-clock HH:MM.
  const m = iso.match(/T(\d{2}:\d{2})/);
  return m ? m[1] : '--:--';
}

function pad(str, len) {
  str = String(str);
  return str.length >= len ? str : str + ' '.repeat(len - str.length);
}
function padL(str, len) {
  str = String(str);
  return str.length >= len ? str : ' '.repeat(len - str.length) + str;
}

/** Run one leg and print its table. Returns the cheapest row (or null). */
async function runLeg(fromName, toName, date, adults) {
  const [from, to] = await Promise.all([resolveStation(fromName), resolveStation(toName)]);
  console.log(`\n${'='.repeat(72)}`);
  console.log(`${fromName}  ->  ${toName}   ${date}   (${adults} adult${adults === 1 ? '' : 's'})`);
  console.log(`  resolved: "${from.name}" (${from.id})  ->  "${to.name}" (${to.id})`);
  console.log('='.repeat(72));

  const raw = await searchFares({
    departureLocationId: from.id,
    arrivalLocationId: to.id,
    date,
    adults,
  });
  const rows = raw.map((r) => normalizeSolution(r, adults)).filter((r) => r.dep);
  const priced = rows.filter((r) => r.amount != null);

  if (rows.length === 0) {
    console.log('  No departures returned for that date.');
    return null;
  }

  // earliest departure (by wall clock) among priced rows
  const earliest = priced.reduce(
    (a, b) => (a == null || b.dep < a.dep ? b : a),
    null
  );
  // sort by price ascending; unpriced (sold out / no fare) sink to the bottom
  const sorted = [...rows].sort((a, b) => {
    if (a.amount == null && b.amount == null) return a.dep < b.dep ? -1 : 1;
    if (a.amount == null) return 1;
    if (b.amount == null) return -1;
    return a.amount - b.amount;
  });
  const cheapest = priced.length ? sorted.find((r) => r.amount != null) : null;

  // header
  console.log(
    '  ' +
      pad('Depart', 8) +
      pad('Arrive', 8) +
      pad('Duration', 10) +
      pad('Train(s)', 16) +
      pad('Changes', 9) +
      padL('Total', 10) +
      padL('/person', 10) +
      '  Notes'
  );
  console.log('  ' + '-'.repeat(78));

  for (const r of sorted) {
    const total = r.amount == null ? '—' : `${r.amount.toFixed(2)}${r.currency}`;
    const per = r.perPerson == null ? '—' : `${r.perPerson.toFixed(2)}${r.currency}`;
    const notes = [];
    if (r === cheapest) notes.push('<= CHEAPEST');
    if (r === earliest) notes.push('(earliest)');
    if (r.amount == null) notes.push(r.status === 'SOLD_OUT' ? 'sold out' : 'no advance fare');
    if (r.indicative) notes.push('indicative');
    console.log(
      '  ' +
        pad(hhmm(r.dep), 8) +
        pad(hhmm(r.arr), 8) +
        pad(r.duration, 10) +
        pad(r.trains.join('+') || '?', 16) +
        pad(String(r.changes), 9) +
        padL(total, 10) +
        padL(per, 10) +
        '  ' +
        notes.join('  ')
    );
  }

  if (cheapest) {
    console.log(
      `\n  Cheapest: ${hhmm(cheapest.dep)} -> ${hhmm(cheapest.arr)}  ` +
        `${cheapest.trains.join('+')}  ${cheapest.amount.toFixed(2)}${cheapest.currency} ` +
        `total  (${cheapest.perPerson.toFixed(2)}${cheapest.currency}/person)`
    );
  } else {
    console.log('\n  No bookable advance fares found for this date.');
  }
  return cheapest;
}

// ---------------------------------------------------------------------------
// Browser fallback (only needed if DataDome starts blocking plain fetch)
// ---------------------------------------------------------------------------

/*
 * If plain fetch ever starts returning 403 / a DataDome HTML challenge,
 * paste the snippet below into the chrome-devtools MCP `evaluate_script`
 * tool while a real, logged-in www.lefrecce.it tab is focused. Because the
 * request then runs same-origin from the page context, it carries the live
 * DataDome cookie and passes the bot wall. It returns the same JSON this
 * script parses, which you can hand back for local formatting.
 */
function buildBrowserSnippet({ departureLocationId, arrivalLocationId, date, adults }) {
  return `
// Run INSIDE a logged-in www.lefrecce.it tab (chrome-devtools evaluate_script).
// Same-origin fetch => carries DataDome cookie => bypasses the bot wall.
(async () => {
  const body = {
    departureLocationId: ${departureLocationId},
    arrivalLocationId: ${arrivalLocationId},
    departureTime: ${JSON.stringify(`${date}T00:00:00.000`)},
    adults: ${adults}, children: 0,
    criteria: { frecceOnly:false, regionalOnly:false, noChanges:false, order:"DEPARTURE_DATE", limit:20, offset:0 },
    advancedSearchRequest: { bestFare: false }
  };
  const r = await fetch("${SOLUTIONS_URL}", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify(body),
    credentials: "include"
  });
  const j = await r.json();
  // Return a compact cheapest-per-departure summary:
  return (j.solutions || []).map(e => ({
    depart: e.solution.departureTime,
    arrive: e.solution.arrivalTime,
    duration: e.solution.duration,
    trains: (e.solution.trains||[]).map(t => t.acronym),
    total: e.solution.price && e.solution.price.amount,
    currency: e.solution.price && e.solution.price.currency
  })).sort((a,b) => (a.total??1e9) - (b.total??1e9));
})();
`.trim();
}

function printBrowserHelp() {
  console.log(`
DataDome fallback — running fares from a real browser tab
=========================================================
The default plain-fetch path worked in testing (HTTP 200, real JSON). Use this
ONLY if you start getting HTTP 403 or an HTML/CAPTCHA challenge instead of JSON.

Steps:
  1. Open https://www.lefrecce.it in your real Chrome and (ideally) log in.
  2. Use the chrome-devtools MCP \`evaluate_script\` tool against that tab.
  3. Paste the snippet below (edit the ids/date/adults). It runs same-origin,
     so it carries the live DataDome cookie and returns fare JSON.

Get station ids first (these GETs are lighter and usually pass even when POST
is challenged):
  ${LOCATIONS_URL}?name=Milano%20Centrale&limit=10

Example snippet (Milano Centrale -> Roma Termini, 2026-09-13, 6 adults):
`);
  console.log(
    buildBrowserSnippet({
      departureLocationId: 830001700,
      arrivalLocationId: 830008409,
      date: '2026-09-13',
      adults: 6,
    })
  );
  console.log('');
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
async function main() {
  const argv = process.argv.slice(2);

  if (argv.includes('--browser-help')) {
    printBrowserHelp();
    return;
  }

  try {
    if (argv.includes('--all-legs')) {
      const adults = ADULTS_DEFAULT;
      console.log(`Trenitalia advance fares — all ${LEGS.length} legs, ${adults} adults`);
      const summary = [];
      for (const leg of LEGS) {
        const cheapest = await runLeg(leg.from, leg.to, leg.date, adults);
        summary.push({ leg, cheapest });
      }
      console.log(`\n${'#'.repeat(72)}`);
      console.log('TRIP SUMMARY — cheapest advance fare per leg');
      console.log('#'.repeat(72));
      let grand = 0;
      let allPriced = true;
      for (const { leg, cheapest } of summary) {
        if (cheapest) {
          grand += cheapest.amount;
          console.log(
            `  ${pad(leg.date, 12)}${pad(`${leg.from} -> ${leg.to}`, 42)}` +
              padL(`${cheapest.amount.toFixed(2)}€`, 10)
          );
        } else {
          allPriced = false;
          console.log(`  ${pad(leg.date, 12)}${pad(`${leg.from} -> ${leg.to}`, 42)}${padL('—', 10)}`);
        }
      }
      console.log('  ' + '-'.repeat(64));
      console.log(
        `  ${pad('', 54)}${padL(`${grand.toFixed(2)}€`, 10)}` +
          (allPriced ? '' : '  (partial — some legs had no fare)')
      );
      return;
    }

    // Single-leg mode
    const [from, to, date, adultsArg] = argv;
    if (!from || !to || !date) {
      console.error(
        'Usage:\n' +
          '  node train-fares.mjs "<origin>" "<destination>" <YYYY-MM-DD> [adults]\n' +
          '  node train-fares.mjs --all-legs\n' +
          '  node train-fares.mjs --browser-help'
      );
      process.exitCode = 1;
      return;
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      console.error(`Date must be YYYY-MM-DD, got "${date}".`);
      process.exitCode = 1;
      return;
    }
    const adults = adultsArg ? parseInt(adultsArg, 10) : ADULTS_DEFAULT;
    await runLeg(from, to, date, adults);
  } catch (e) {
    if (e instanceof BlockedError) {
      console.error(`\n${e.message}\n`);
      process.exitCode = 2;
    } else {
      console.error(`Error: ${e.message}`);
      process.exitCode = 1;
    }
  }
}

main();
