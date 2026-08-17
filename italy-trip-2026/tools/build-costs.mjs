/* build-costs.mjs — public/costs.csv  →  the `fixed:` ledger in public/costs-data.js
 *
 * The CSV is the source of truth for the ledger rows. Edit it in a spreadsheet,
 * export back over public/costs.csv, then run:
 *
 *     node tools/build-costs.mjs
 *
 * Only the `fixed: [ ... ]` block is rewritten. budgetUSD, days, people, the
 * sliders and dinnerModel are left exactly as they are, so live tuning of the
 * model never gets clobbered by a ledger update.
 *
 * CSV columns: id, Category, Item, Amount USD, Status, Note, URL
 *   - Amount USD blank  → usd:null  (booked but amount not entered yet)
 *   - Status            → 'booked' | 'estimate'
 *   - Note / URL blank  → key omitted
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CSV = path.join(ROOT, 'public', 'costs.csv');
const JS = path.join(ROOT, 'public', 'costs-data.js');

// ── minimal RFC-4180 parser (handles quoted fields, "" escapes, embedded commas/newlines) ──
function parseCSV(text) {
  const rows = [];
  let row = [], field = '', inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else if (c !== '\r') field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows.filter(r => r.some(v => v !== ''));
}

const rows = parseCSV(fs.readFileSync(CSV, 'utf8'));
const header = rows.shift().map(h => h.trim().toLowerCase());
const col = name => {
  const i = header.indexOf(name);
  if (i === -1) throw new Error(`costs.csv is missing the "${name}" column`);
  return i;
};
const [iId, iCat, iItem, iUsd, iStatus, iNote, iUrl] =
  ['id', 'category', 'item', 'amount usd', 'status', 'note', 'url'].map(col);

const esc = s => String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'");

const lines = rows.map((r, n) => {
  const id = r[iId].trim();
  if (!id) throw new Error(`row ${n + 2} of costs.csv has no id`);
  const status = r[iStatus].trim() || 'estimate';
  if (!['booked', 'estimate'].includes(status))
    throw new Error(`row ${n + 2} ("${id}"): status must be booked or estimate, got "${status}"`);

  const raw = r[iUsd].trim().replace(/[$,]/g, '');
  let usd = 'null';
  if (raw !== '') {
    const n2 = Number(raw);
    if (!Number.isFinite(n2)) throw new Error(`row ${n + 2} ("${id}"): "${r[iUsd]}" is not a number`);
    usd = String(n2);
  }

  let s = `    { id:'${esc(id)}', cat:'${esc(r[iCat].trim())}', label:'${esc(r[iItem].trim())}', usd:${usd}, status:'${status}'`;
  if (r[iNote].trim()) s += `, note:'${esc(r[iNote].trim())}'`;
  if (r[iUrl].trim()) s += `, url:'${esc(r[iUrl].trim())}'`;
  return s + ' },';
});

const js = fs.readFileSync(JS, 'utf8');
// Replace everything between "fixed: [" and the closing "]," at the same indent.
const re = /( {2}fixed: \[\n)[\s\S]*?(\n {2}\],)/;
if (!re.test(js)) throw new Error('could not locate the `fixed: [ ... ],` block in costs-data.js');
const out = js.replace(re, (_m, open, close) => open + lines.join('\n') + close);

fs.writeFileSync(JS, out);

const booked = rows.filter(r => r[iStatus].trim() === 'booked')
  .reduce((s, r) => s + (Number(r[iUsd].replace(/[$,]/g, '')) || 0), 0);
const total = rows.reduce((s, r) => s + (Number(r[iUsd].replace(/[$,]/g, '')) || 0), 0);
console.log(`costs-data.js rebuilt — ${rows.length} rows`);
console.log(`  booked  $${booked.toFixed(2)}`);
console.log(`  total   $${total.toFixed(2)}`);
