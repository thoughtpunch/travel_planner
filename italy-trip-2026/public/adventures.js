/* Per-city "Adventures for the crew" grid, injected on each city page (like
   photos.js). Data lives in /adventures-data.js as window.TRIP_ADVENTURES[key].
   Self-contained, no deps. Photos are optional & freely-licensed (Wikimedia);
   if one fails to load it's replaced by an emoji tile, never a broken image. */
(function () {
  if (!window.TRIP_ADVENTURES) return;

  function norm(p) {
    if (!p) return '/';
    p = p.replace(/\.html$/, '').replace(/\/index$/, '/');
    if (p.length > 1 && p.charAt(p.length - 1) === '/') p = p.slice(0, -1);
    return p === '' ? '/' : p;
  }
  var key = norm(location.pathname).replace(/^\//, '');
  var items = window.TRIP_ADVENTURES[key];
  if (!items || !items.length) return;

  var PAL = { cream:'#F5F0E8', warm:'#FDFAF4', ink:'#1A1510', terra:'#C4531A',
              ochre:'#D4920A', stone:'#8C7B6B', rule:'#C4B9A8' };

  // category → [emoji, accent]
  var CATS = {
    castle:['🏰','#7B5EA7'], underground:['🕳️','#5C6B73'], maze:['🌀','#2E7D6B'],
    caves:['🦇','#4A5568'], thrill:['🧗','#C4531A'], transport:['🚡','#3D7EA6'],
    machines:['⚙️','#6B7280'], craft:['🛠️','#B7791F'], food:['🍕','#C05621'],
    weird:['💀','#805AD5'], hunt:['🗺️','#2F855A'], water:['🚣','#2B7A9B'],
    architecture:['🏛️','#9C6B3F'], abandoned:['👻','#4A5568'], animals:['🦅','#8B6F1F'],
    secret:['🔑','#975A16'], whoa:['😮','#C4531A'], rock:['🪨','#8C6239'],
    mountain:['⛰️','#2C7A7B'], detour:['🚂','#C4531A']
  };
  var WHO = { rhys:['Rhys','#C4531A'], jude:['Jude','#8C6239'], grey:['Grey','#2C7A7B'],
              keir:['Keir','#3D7EA6'], all:['All','#8C7B6B'] };
  var GROUPS = [
    { r:'way',  lbl:'On the way here' },
    { r:'base', lbl:'Right in town' },
    { r:'day',  lbl:'Easy day-trips' }
  ];

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  var css =
    '.adv-wrap{max-width:1080px;margin:0 auto;padding:60px 40px 8px}' +
    ".adv-lbl{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:"+PAL.stone+";margin-bottom:14px}" +
    ".adv-ttl{font-family:'Playfair Display',serif;font-size:clamp(24px,4vw,38px);font-weight:700;line-height:1.1;margin-bottom:10px;color:"+PAL.ink+"}" +
    ".adv-ttl em{font-style:italic;color:"+PAL.terra+";font-weight:400}" +
    ".adv-intro{font-family:'DM Sans',sans-serif;font-size:15px;color:"+PAL.ink+";opacity:.8;max-width:640px;margin-bottom:6px}" +
    ".adv-grouplbl{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:"+PAL.terra+";margin:34px 0 14px;padding-bottom:6px;border-bottom:1px solid "+PAL.rule+"}" +
    '.adv-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}' +
    '.adv-card{background:'+PAL.warm+';border:1px solid '+PAL.rule+';border-radius:4px;overflow:hidden;display:flex;flex-direction:column;position:relative}' +
    '.adv-star{position:absolute;top:8px;right:9px;z-index:2;font-size:13px;background:rgba(26,21,16,.72);color:'+PAL.ochre+';border-radius:20px;padding:1px 7px 2px;letter-spacing:.5px;font-family:"DM Mono",monospace;font-size:9px}' +
    '.adv-thumb{height:132px;position:relative;display:block;overflow:hidden}' +
    '.adv-thumb img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s ease}' +
    '.adv-card:hover .adv-thumb img{transform:scale(1.06)}' +
    '.adv-emoji{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:44px}' +
    '.adv-body{padding:12px 14px 14px;display:flex;flex-direction:column;gap:7px;flex:1}' +
    ".adv-name{font-family:'Playfair Display',serif;font-size:16px;font-weight:700;line-height:1.18;color:"+PAL.ink+"}" +
    ".adv-blurb{font-family:'DM Sans',sans-serif;font-size:12.5px;line-height:1.45;color:"+PAL.ink+";opacity:.82;flex:1}" +
    '.adv-chips{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin-top:2px}' +
    ".adv-chip{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.5px;color:#fff;border-radius:20px;padding:2px 8px;text-transform:uppercase}" +
    ".adv-link{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:"+PAL.terra+";text-decoration:none;border-bottom:1px solid "+PAL.rule+";align-self:flex-start;padding-bottom:1px}" +
    ".adv-link:hover{color:"+PAL.ochre+";border-color:"+PAL.ochre+"}" +
    ".adv-foot{font-family:'DM Sans',sans-serif;font-size:13px;color:"+PAL.ink+";opacity:.7;margin-top:26px}" +
    ".adv-foot a{color:"+PAL.terra+";text-decoration:none;border-bottom:1px solid "+PAL.rule+"}" +
    '@media(max-width:520px){.adv-wrap{padding-left:20px;padding-right:20px}.adv-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var sec = document.createElement('section');
  sec.className = 'adv-wrap';
  var html =
    '<div class="adv-lbl">— For Rhys · Jude · Grey · Keir</div>' +
    '<h2 class="adv-ttl">Adventures <em>for the crew</em></h2>' +
    '<p class="adv-intro">Hand-picked things near this stop that each of you would actually love — caves, castles, workshops, weird museums, quarries, mazes and mountains. ★ = extra-high adventure.</p>';

  GROUPS.forEach(function (grp) {
    var list = items.filter(function (it) { return (it.r || 'base') === grp.r; });
    if (!list.length) return;
    html += '<div class="adv-grouplbl">' + grp.lbl + '</div><div class="adv-grid">';
    list.forEach(function (it) {
      var cat = CATS[it.c] || ['✨', PAL.stone];
      var thumb = it.img
        ? '<a class="adv-thumb" style="background:' + cat[1] + '"><img loading="lazy" decoding="async" alt="' + esc(it.n) + '" src="' + esc(it.img) + '" onerror="this.parentNode.innerHTML=\'<div class=&quot;adv-emoji&quot; style=&quot;background:' + cat[1] + '&quot;>' + cat[0] + '</div>\'"></a>'
        : '<div class="adv-thumb"><div class="adv-emoji" style="background:' + cat[1] + '">' + cat[0] + '</div></div>';
      var chips = (it.w || []).map(function (w) {
        var k = WHO[w] || [w, PAL.stone];
        return '<span class="adv-chip" style="background:' + k[1] + '">' + esc(k[0]) + '</span>';
      }).join('');
      html += '<div class="adv-card">' +
        (it.s ? '<div class="adv-star">★ must</div>' : '') +
        thumb +
        '<div class="adv-body">' +
          '<div class="adv-name">' + esc(it.n) + '</div>' +
          '<div class="adv-blurb">' + esc(it.b) + '</div>' +
          '<div class="adv-chips">' + chips + '</div>' +
          (it.l ? '<a class="adv-link" href="' + esc(it.l) + '" target="_blank" rel="noopener">Book / info →</a>' : '') +
        '</div>' +
      '</div>';
    });
    html += '</div>';
  });

  html += '<p class="adv-foot">This is the shortlist for this stop. The full menu — ~150 places across the whole trip, sortable by kid — lives in <a href="/adventures.csv" download>adventures.csv</a>.</p>';
  sec.innerHTML = html;

  var footer = document.querySelector('footer');
  var main = document.querySelector('main');
  if (footer && footer.parentNode) footer.parentNode.insertBefore(sec, footer);
  else if (main) main.appendChild(sec);
  else document.body.appendChild(sec);
})();
