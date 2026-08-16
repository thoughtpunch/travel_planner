// Simple HTTP Basic Auth gate for the whole site (Vercel Edge Middleware).
// Runs at the edge before any static file is served. Creds are shared/simple —
// this is light gating over HTTPS, not high security.
// Gate everything EXCEPT the /api functions (those are same-origin data
// endpoints, guarded by their own shared secret) and static assets.
export const config = { matcher: ['/((?!api/).*)'] };

const USER = 'barrett';
const PASS = 'italytrip';

export default function middleware(request) {
  const auth = request.headers.get('authorization') || '';
  if (auth.startsWith('Basic ')) {
    try {
      const [user, pass] = atob(auth.slice(6)).split(':');
      if (user === USER && pass === PASS) return; // authorized → continue to the site
    } catch (e) { /* fall through to 401 */ }
  }
  return new Response('Authentication required.', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Italy 2026", charset="UTF-8"' },
  });
}
