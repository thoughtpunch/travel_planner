// Shared Google auth + Sheets helpers for the api/ functions.
// Underscore-prefixed → Vercel treats this as a support file, not a route.
// Uses a service-account JWT (RS256) signed with node:crypto — no npm deps.
import crypto from 'node:crypto';

function b64url(buf) {
  return Buffer.from(buf).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}

let cache = { token: null, exp: 0 };

export async function getToken() {
  const now = Math.floor(Date.now() / 1000);
  if (cache.token && cache.exp - 60 > now) return cache.token;
  const sa = JSON.parse(process.env.GOOGLE_SA);
  const header = b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claim = b64url(JSON.stringify({
    iss: sa.client_email,
    scope: 'https://www.googleapis.com/auth/spreadsheets',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now, exp: now + 3600,
  }));
  const signer = crypto.createSign('RSA-SHA256');
  signer.update(header + '.' + claim); signer.end();
  const sig = b64url(signer.sign(sa.private_key));
  const jwt = header + '.' + claim + '.' + sig;
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion: jwt }),
  });
  const j = await res.json();
  if (!j.access_token) throw new Error('token: ' + JSON.stringify(j));
  cache = { token: j.access_token, exp: now + (j.expires_in || 3600) };
  return cache.token;
}

export async function sheets(path, opts = {}) {
  const token = await getToken();
  const res = await fetch('https://sheets.googleapis.com/v4/spreadsheets/' + path, {
    ...opts,
    headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json', ...(opts.headers || {}) },
  });
  const txt = await res.text();
  if (!res.ok) throw new Error('sheets ' + res.status + ': ' + txt);
  try { return txt ? JSON.parse(txt) : {}; } catch (e) { return { raw: txt }; }
}

export async function firstTab(id) {
  const meta = await sheets(id + '?fields=sheets.properties.title');
  return (meta.sheets && meta.sheets[0] && meta.sheets[0].properties.title) || 'Sheet1';
}

export const COLS = ['id', 'leg', 'city', 'region', 'title', 'ideal_for', 'category',
  'reach', 'cost', 'how_to_get_there', 'website', 'status', 'notes', 'updated'];
