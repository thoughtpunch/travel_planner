// POST /api/save  { secret, id, title, leg, city, status, notes }
// Upserts the row (keyed by id) in the DB sheet: sets status/notes/updated.
// Same-origin from the (basic-auth'd) page; guarded by a shared secret.
import { sheets, firstTab, COLS } from './_google.js';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, reason: 'method' });
  try {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body || '{}'); } catch { body = {}; } }
    if (!body || typeof body !== 'object') body = {};
    if (!process.env.SAVE_SECRET || body.secret !== process.env.SAVE_SECRET)
      return res.status(403).json({ ok: false, reason: 'forbidden' });
    const id = process.env.SHEET_ID;
    if (!process.env.GOOGLE_SA || !id) return res.status(200).json({ ok: false, reason: 'not_configured' });
    if (!body.id) return res.status(400).json({ ok: false, reason: 'no_id' });

    const tab = await firstTab(id);
    const rng = encodeURIComponent(tab);
    const cur = await sheets(id + '/values/' + rng + '!A1:N');
    const rows = cur.values || [];
    let head = rows[0] || [];
    if (head.length === 0) {
      await sheets(id + '/values/' + rng + '!A1?valueInputOption=RAW',
        { method: 'PUT', body: JSON.stringify({ values: [COLS] }) });
      head = COLS;
    }
    const ix = {}; head.forEach((h, i) => ix[h] = i);
    const now = new Date().toISOString();

    let rowNum = -1;
    for (let i = 1; i < rows.length; i++) { if ((rows[i] || [])[ix.id] === body.id) { rowNum = i + 1; break; } }

    const vals = new Array(head.length).fill('');
    if (rowNum > 0) { const ex = rows[rowNum - 1] || []; for (let i = 0; i < head.length; i++) vals[i] = ex[i] || ''; }
    const set = (k, v) => { if (ix[k] != null && v != null) vals[ix[k]] = String(v); };
    set('id', body.id); if (body.leg != null) set('leg', body.leg); if (body.city) set('city', body.city);
    if (body.title) set('title', body.title);
    set('status', body.status || ''); set('notes', body.notes || ''); set('updated', now);

    if (rowNum > 0) {
      await sheets(id + '/values/' + rng + '!A' + rowNum + '?valueInputOption=RAW',
        { method: 'PUT', body: JSON.stringify({ values: [vals] }) });
    } else {
      await sheets(id + '/values/' + rng + '!A1:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS',
        { method: 'POST', body: JSON.stringify({ values: [vals] }) });
    }
    res.status(200).json({ ok: true, updated: now });
  } catch (e) {
    res.status(200).json({ ok: false, reason: String(e.message || e) });
  }
}
