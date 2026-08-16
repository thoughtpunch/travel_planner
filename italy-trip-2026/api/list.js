// GET /api/list → { ok, items:[{id,status,notes,updated}] } from the DB sheet.
// Always 200 so the client can degrade gracefully to localStorage.
import { sheets, firstTab } from './_google.js';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  try {
    const id = process.env.SHEET_ID;
    if (!process.env.GOOGLE_SA || !id) return res.status(200).json({ ok: false, reason: 'not_configured' });
    const tab = await firstTab(id);
    const r = await sheets(id + '/values/' + encodeURIComponent(tab) + '!A1:N?majorDimension=ROWS');
    const rows = r.values || [];
    const head = rows[0] || [];
    const ix = {}; head.forEach((h, i) => ix[h] = i);
    const items = rows.slice(1).map(row => ({
      id: row[ix.id], status: row[ix.status] || '', notes: row[ix.notes] || '', updated: row[ix.updated] || '',
    })).filter(x => x.id && (x.status || x.notes));
    res.status(200).json({ ok: true, items });
  } catch (e) {
    res.status(200).json({ ok: false, reason: String(e.message || e) });
  }
}
