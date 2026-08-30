/* ============================================================================
 * leg-budget.js — injects a "what this leg costs" snapshot into each city page.
 * ----------------------------------------------------------------------------
 * Self-injecting, same pattern as photos.js: it matches window.location.pathname
 * against the `page` field in leg-budgets.js and does nothing on pages with no
 * matching leg. Include it (with leg-budgets.js) on any city page.
 *
 *   <script src="/leg-budgets.js" defer></script>
 *   <script src="/leg-budget.js" defer></script>
 *
 * All figures are for the WHOLE PARTY in EUR, with USD alongside. Lodging is the
 * real booked amount, so it never varies across low/avg/high — everything else
 * is a modelled band.
 * ==========================================================================*/
(function () {
  if (!window.LEG_BUDGETS) return;

  function norm(p) {
    if (!p) return '/';
    p = p.replace(/\.html$/, '').replace(/\/index$/, '/');
    if (p.length > 1 && p.charAt(p.length - 1) === '/') p = p.slice(0, -1);
    return p === '' ? '/' : p;
  }
  var here = norm(location.pathname);
  var B = null;
  for (var i = 0; i < window.LEG_BUDGETS.length; i++)
    if (window.LEG_BUDGETS[i].page === here) { B = window.LEG_BUDGETS[i]; break; }
  if (!B) return;

  var RATE = window.EUR_USD || 1.16;
  var eur = function (n) { return '€' + Math.round(n).toLocaleString('en-US'); };
  var usd = function (n) { return '$' + Math.round(n * RATE).toLocaleString('en-US'); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c];
    });
  };

  var css = document.createElement('style');
  css.textContent = [
    '.lb-wrap{border-top:2px solid var(--ink);padding:56px 0 24px}',
    '.lb-kicker{font-family:"DM Mono",monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--terra);margin-bottom:10px}',
    '.lb-h{font-family:"Playfair Display",serif;font-size:clamp(24px,3.4vw,36px);font-weight:900;line-height:1.1;margin-bottom:6px}',
    '.lb-h em{font-style:italic;color:var(--terra);font-weight:400}',
    '.lb-sub{font-size:14.5px;color:var(--stone);max-width:640px;margin-bottom:20px;line-height:1.5}',
    '.lb-heroes{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}',
    '.lb-hero{background:var(--warm-white);border:1px solid var(--rule);border-radius:8px;padding:14px 15px}',
    '.lb-hero .n{font-family:"DM Mono",monospace;font-size:26px;font-weight:500;letter-spacing:-.5px;line-height:1.1}',
    '.lb-hero .u{font-family:"DM Mono",monospace;font-size:11px;color:var(--stone);margin-top:2px}',
    '.lb-hero .l{font-family:"DM Mono",monospace;font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--stone);margin-top:7px}',
    '.lb-hero.avg{border-color:var(--terra);border-left-width:3px}',
    '.lb-hero.avg .n{color:var(--terra)}',
    '.lb-tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}',
    '.lb-t{width:100%;border-collapse:collapse;font-size:13.5px;min-width:440px}',
    '.lb-t th{font-family:"DM Mono",monospace;font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;',
    '  color:var(--stone);text-align:right;padding:8px 10px;border-bottom:1px solid var(--rule)}',
    '.lb-t th:first-child{text-align:left}',
    '.lb-t td{padding:9px 10px;border-bottom:1px solid var(--rule);text-align:right;',
    '  font-family:"DM Mono",monospace;font-variant-numeric:tabular-nums}',
    '.lb-t td:first-child{text-align:left;font-family:"DM Sans",sans-serif}',
    '.lb-t .avgcol{color:var(--terra);font-weight:500}',
    '.lb-badge{font-family:"DM Mono",monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;',
    '  border-radius:3px;padding:1px 5px;margin-left:7px;vertical-align:middle;white-space:nowrap}',
    '.lb-badge.paid{background:rgba(107,142,90,.22);color:#3f5c30}',
    '.lb-badge.booked{background:rgba(107,142,90,.16);color:#4f6b3f}',
    '.lb-badge.part-paid{background:rgba(212,160,23,.2);color:#8a6400}',
    '.lb-badge.to-book{background:rgba(196,83,26,.16);color:#a8461a}',
    '.lb-t tr.tot td{border-top:2px solid var(--ink);border-bottom:none;font-weight:600;padding-top:11px}',
    '.lb-note{display:block;font-family:"DM Sans",sans-serif;font-size:11px;color:var(--stone);',
    '  margin-top:2px;line-height:1.35;font-weight:400}',
    '.lb-sl{margin-top:18px;background:var(--warm-white);border:1px solid var(--rule);',
    '  border-left:3px solid var(--ochre);border-radius:8px;padding:13px 15px}',
    '.lb-sl .t{font-family:"DM Mono",monospace;font-size:9.5px;letter-spacing:1.2px;',
    '  text-transform:uppercase;color:var(--ochre);margin-bottom:6px}',
    '.lb-sl ul{margin:0;padding-left:18px}',
    '.lb-sl li{font-size:13.5px;margin-bottom:3px}',
    '.lb-sl .c{font-family:"DM Mono",monospace;font-size:11.5px;color:var(--stone)}',
    '.lb-foot{font-size:12px;color:var(--stone);margin-top:14px;line-height:1.5}',
    '@media(max-width:640px){',
    '  .lb-wrap{padding:40px 0 18px}',
    '  .lb-heroes{grid-template-columns:1fr 1fr;gap:9px}',
    '  .lb-hero{padding:11px 12px}.lb-hero .n{font-size:21px}',
    '  .lb-t{font-size:12.5px}.lb-t td,.lb-t th{padding:7px 7px}',
    '}'
  ].join('');
  document.head.appendChild(css);

  var s = document.createElement('section');
  s.className = 'lb-wrap';
  s.id = 'leg-budget';

  var h = '';
  h += '<div class="lb-kicker">— What this leg costs</div>';
  h += '<h2 class="lb-h">' + esc(B.city) + ' <em>budget snapshot</em></h2>';
  h += '<p class="lb-sub">' + esc(B.dates) + ' · <strong>' + B.nights + ' night' + (B.nights === 1 ? '' : 's') +
       '</strong> · ' + B.people + ' people. Every figure is the <strong>total for the whole party</strong>, not per person. ' +
       'Lodging is the real booked amount; the rest is a low/average/high band.</p>';

  h += '<div class="lb-heroes">' +
    '<div class="lb-hero"><div class="n">' + eur(B.spend.lo) + '</div><div class="u">' + usd(B.spend.lo) + '</div><div class="l">Lean</div></div>' +
    '<div class="lb-hero avg"><div class="n">' + eur(B.spend.avg) + '</div><div class="u">' + usd(B.spend.avg) + '</div><div class="l">Likely</div></div>' +
    '<div class="lb-hero"><div class="n">' + eur(B.spend.hi) + '</div><div class="u">' + usd(B.spend.hi) + '</div><div class="l">Loose</div></div>' +
    '<div class="lb-hero"><div class="n">' + eur(B.perDay.avg) + '</div><div class="u">' + usd(B.perDay.avg) + ' / day</div><div class="l">Per day, likely</div></div>' +
    '</div>';

  h += '<div class="lb-tablewrap"><table class="lb-t"><thead><tr>' +
       '<th>Category</th><th>Lean</th><th>Likely</th><th>Loose</th></tr></thead><tbody>';
  for (var r = 0; r < B.rows.length; r++) {
    var row = B.rows[r];
    var badge = row.badge ? '<span class="lb-badge ' + row.badge.replace(/ /g, '-') + '">' + esc(row.badge) + '</span>' : '';
    h += '<tr' + (row.fixed ? ' class="fixed"' : '') + '>' +
      '<td>' + esc(row.label) + badge + (row.note ? '<span class="lb-note">' + esc(row.note) + '</span>' : '') + '</td>' +
      '<td>' + eur(row.lo) + '</td>' +
      '<td class="avgcol">' + eur(row.avg) + '</td>' +
      '<td>' + eur(row.hi) + '</td></tr>';
  }
  h += '<tr class="tot"><td>All-in for this leg</td><td>' + eur(B.total.lo) + '</td>' +
       '<td class="avgcol">' + eur(B.total.avg) + '</td><td>' + eur(B.total.hi) + '</td></tr>';
  h += '<tr class="tot" style="border-top:none"><td style="font-weight:400;color:var(--stone)">' +
       'Still to spend <span class="lb-note">excludes the lodging above, which is already booked</span></td>' +
       '<td>' + usd(B.spend.lo) + '</td><td class="avgcol">' + usd(B.spend.avg) + '</td><td>' + usd(B.spend.hi) + '</td></tr>';
  h += '</tbody></table></div>';

  if (B.shortlist && B.shortlist.length) {
    h += '<div class="lb-sl"><div class="t">On the shortlist for this leg</div><ul>';
    for (var k = 0; k < B.shortlist.length; k++)
      h += '<li>' + esc(B.shortlist[k].n) + ' <span class="c">' + eur(B.shortlist[k].eur) +
           ' · ' + usd(B.shortlist[k].eur) + '</span></li>';
    h += '</ul></div>';
  }

  h += '<p class="lb-foot">Converted at €1 ≈ $' + RATE.toFixed(2) + '. ' +
       'Activity prices are researched 2026 rates for this exact party — under-18s free where Italian state museums make them free. ' +
       'Full ledger on <a href="/costs" style="color:var(--terra)">Costs</a> · every option on ' +
       '<a href="/adventures?leg=' + B.leg + '" style="color:var(--terra)">Adventures</a>.</p>';

  s.innerHTML = h;

  var main = document.querySelector('main');
  if (main) main.appendChild(s);
  else document.body.appendChild(s);
})();
