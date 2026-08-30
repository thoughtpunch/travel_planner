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
 * CSV columns: id, Category, Item, Amount USD, Status, Note, URL,
 *              Paid USD, Paid Date, Pay Ref, Pay Status
 *   - Amount USD blank  → usd:null  (booked but amount not entered yet)
 *   - Status            → 'booked' | 'estimate'      (is the COST real yet?)
 *   - Pay Status        → 'paid' | 'partial' | 'pending' | 'unknown'
 *                         (has the MONEY actually left the account yet?)
 *                         Defaults to 'unknown' when the column is absent/blank,
 *                         which is deliberate: unknown is a to-do, not a zero.
 *   - Paid USD blank    → paidUsd:0 for pending, null for unknown
 *   - Note / URL / Paid Date / Pay Ref blank → key omitted
 *
 * The four payment columns are OPTIONAL — an older 7-column export still builds,
 * with every row falling back to 'unknown'.
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

// Payment columns are optional — -1 means "not in this export".
const optCol = name => header.indexOf(name);
const [iPaid, iPaidDate, iPayRef, iPayStatus, iDue] =
  ['paid usd', 'paid date', 'pay ref', 'pay status', 'due date'].map(optCol);
const cell = (r, i) => (i === -1 ? '' : (r[i] || '').trim());

const PAY_STATES = ['paid', 'partial', 'pending', 'unknown'];

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

  // ── payment state ──────────────────────────────────────────────────────
  const pay = cell(r, iPayStatus) || 'unknown';
  if (!PAY_STATES.includes(pay))
    throw new Error(`row ${n + 2} ("${id}"): pay status must be one of ${PAY_STATES.join('|')}, got "${pay}"`);

  const paidRaw = cell(r, iPaid).replace(/[$,]/g, '');
  let paidUsd;
  if (paidRaw !== '') {
    const p = Number(paidRaw);
    if (!Number.isFinite(p)) throw new Error(`row ${n + 2} ("${id}"): paid "${cell(r, iPaid)}" is not a number`);
    paidUsd = p;
  } else if (pay === 'paid') {
    paidUsd = usd === 'null' ? null : Number(usd);   // paid in full ⇒ paid == amount
  } else if (pay === 'pending') {
    paidUsd = 0;                                     // known to be nothing yet
  } else {
    paidUsd = null;                                  // unknown ⇒ genuinely unknown, not 0
  }
  if (pay === 'partial' && paidUsd == null)
    throw new Error(`row ${n + 2} ("${id}"): pay status "partial" needs a Paid USD amount`);
  if (pay === 'paid' && paidUsd != null && usd !== 'null' && Math.abs(paidUsd - Number(usd)) > 1)
    console.warn(`  ⚠︎ ${id}: marked paid but paid $${paidUsd} ≠ amount $${usd}`);

  let s = `    { id:'${esc(id)}', cat:'${esc(r[iCat].trim())}', label:'${esc(r[iItem].trim())}', usd:${usd}, status:'${status}'`;
  if (r[iNote].trim()) s += `, note:'${esc(r[iNote].trim())}'`;
  if (r[iUrl].trim()) s += `, url:'${esc(r[iUrl].trim())}'`;
  s += `, pay:'${pay}', paidUsd:${paidUsd == null ? 'null' : paidUsd}`;
  if (cell(r, iPaidDate)) s += `, paidDate:'${esc(cell(r, iPaidDate))}'`;
  if (cell(r, iPayRef)) s += `, payRef:'${esc(cell(r, iPayRef))}'`;
  if (cell(r, iDue)) s += `, dueDate:'${esc(cell(r, iDue))}'`;
  return s + ' },';
});

const js = fs.readFileSync(JS, 'utf8');
// Replace everything between "fixed: [" and the closing "]," at the same indent.
const re = /( {2}fixed: \[\n)[\s\S]*?(\n {2}\],)/;
if (!re.test(js)) throw new Error('could not locate the `fixed: [ ... ],` block in costs-data.js');
const out = js.replace(re, (_m, open, close) => open + lines.join('\n') + close);

fs.writeFileSync(JS, out);

const amt = r => Number(r[iUsd].replace(/[$,]/g, '')) || 0;
const booked = rows.filter(r => r[iStatus].trim() === 'booked').reduce((s, r) => s + amt(r), 0);
const total = rows.reduce((s, r) => s + amt(r), 0);

// ── cash position: what has actually left the account vs what hasn't ──
const money = { paid: 0, scheduled: 0, unknown: 0 };
const dues = [];
for (const r of rows) {
  const pay = cell(r, iPayStatus) || 'unknown';
  const a = amt(r);
  const paidRaw = cell(r, iPaid).replace(/[$,]/g, '');
  const paid = paidRaw !== '' ? Number(paidRaw) : (pay === 'paid' ? a : 0);
  if (pay === 'unknown') { money.unknown += a; continue; }
  money.paid += paid;
  const owed = a - paid;
  if (owed > 0.005) {
    money.scheduled += owed;
    dues.push({ id: r[iId].trim(), owed, due: cell(r, iDue) });
  }
}

console.log(`costs-data.js rebuilt — ${rows.length} rows`);
console.log(`  booked          $${booked.toFixed(2)}`);
console.log(`  total           $${total.toFixed(2)}`);
console.log('  ── cash position ──');
console.log(`  already paid    $${money.paid.toFixed(2)}`);
console.log(`  still owed      $${money.scheduled.toFixed(2)}`);
console.log(`  UNKNOWN status  $${money.unknown.toFixed(2)}   <- chase these`);
if (dues.length) {
  console.log('  upcoming charges:');
  dues.sort((a, b) => (a.due || '9999').localeCompare(b.due || '9999'))
    .forEach(d => console.log(`    ${(d.due || 'no date').padEnd(12)} ${d.id.padEnd(18)} $${d.owed.toFixed(2)}`));
}
