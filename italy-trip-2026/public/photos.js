/* Real-place photos, injected on every page (like menu.js).
   Data lives in /photos-data.js as window.TRIP_PHOTOS[pageKey] = { hero, items[] }.
   All images are freely-licensed Wikimedia Commons files, hotlinked from
   upload.wikimedia.org with attribution. Self-contained, no deps.

   Features: responsive Wikimedia thumbnails, lazy-loading, click-to-zoom
   lightbox, graceful onerror (Wikimedia throttles bursts — broken shots are
   hidden, not shown), and a localStorage cache of failed/known URLs so we
   don't re-attempt dead images across pages/visits. */
(function () {
  if (!window.TRIP_PHOTOS) return;

  // ── which page are we on ──
  function norm(p) {
    if (!p) return '/';
    p = p.replace(/\.html$/, '').replace(/\/index$/, '/');
    if (p.length > 1 && p.charAt(p.length - 1) === '/') p = p.slice(0, -1);
    return p === '' ? '/' : p;
  }
  var here = norm(location.pathname);
  var key = here === '/' ? 'home' : here.replace(/^\//, '');
  var data = window.TRIP_PHOTOS[key];
  if (!data) return;

  // ── localStorage cache (failed urls so we skip known-dead images) ──
  var CACHE_KEY = 'tp_photos_v1';
  var cache = { failed: {} };
  try { cache = JSON.parse(localStorage.getItem(CACHE_KEY)) || cache; } catch (e) {}
  if (!cache.failed) cache.failed = {};
  function persist() { try { localStorage.setItem(CACHE_KEY, JSON.stringify(cache)); } catch (e) {} }

  // ── responsive Wikimedia thumbnail URLs (smaller = faster, fewer 429s) ──
  // Wikimedia only serves pre-materialised thumbnail widths (the ones Wikipedia
  // itself uses) from upload.wikimedia.org; requesting a novel width returns 400.
  // So we ship the verified URLs exactly as curated rather than rewriting them.
  function wthumb(url) { return url; }

  var PAL = {
    cream: '#F5F0E8', warm: '#FDFAF4', ink: '#1A1510', terra: '#C4531A',
    ochre: '#D4920A', stone: '#8C7B6B', rule: '#C4B9A8'
  };

  // ── styles ──
  var css =
    '.tp-hero{position:relative;width:100%;height:clamp(220px,38vw,430px);overflow:hidden;background:' + PAL.ink + ';margin:0}' +
    '.tp-hero img{width:100%;height:100%;object-fit:cover;display:block}' +
    '.tp-cap{position:absolute;bottom:0;right:0;background:rgba(26,21,16,.62);color:' + PAL.cream + ';' +
      "font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.5px;padding:4px 9px;max-width:70%;text-align:right}" +
    '.tp-cap a{color:' + PAL.ochre + ';text-decoration:none}' +
    '.tp-gallery{max-width:1080px;margin:0 auto;padding:56px 40px 8px}' +
    '.tp-gallery .tp-lbl{font-family:\'DM Mono\',monospace;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:' + PAL.stone + ';margin-bottom:14px}' +
    ".tp-gallery .tp-ttl{font-family:'Playfair Display',serif;font-size:clamp(24px,4vw,38px);font-weight:700;line-height:1.1;margin-bottom:24px;color:" + PAL.ink + '}' +
    '.tp-gallery .tp-ttl em{font-style:italic;color:' + PAL.terra + ';font-weight:400}' +
    '.tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}' +
    '.tp-shot{margin:0;background:' + PAL.warm + ';border:1px solid ' + PAL.rule + ';overflow:hidden;display:flex;flex-direction:column}' +
    '.tp-shot button{border:0;padding:0;margin:0;background:none;cursor:zoom-in;display:block;width:100%}' +
    '.tp-shot img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;transition:transform .4s ease}' +
    '.tp-shot:hover img{transform:scale(1.05)}' +
    '.tp-shot figcaption{padding:8px 11px 10px}' +
    ".tp-shot .tp-place{font-family:'Playfair Display',serif;font-size:14px;font-weight:700;color:" + PAL.ink + ';line-height:1.2}' +
    ".tp-shot .tp-cred{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.3px;color:" + PAL.stone + ";margin-top:2px}" +
    '.tp-shot .tp-cred a{color:' + PAL.stone + ';text-decoration:none;border-bottom:1px solid ' + PAL.rule + '}' +
    '@media(max-width:520px){.tp-gallery{padding-left:20px;padding-right:20px}.tp-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}' +
    // lightbox
    '#tp-lb{position:fixed;inset:0;z-index:11000;background:rgba(20,16,12,.92);display:none;align-items:center;justify-content:center;flex-direction:column;padding:30px}' +
    '#tp-lb.open{display:flex}' +
    '#tp-lb img{max-width:92vw;max-height:80vh;object-fit:contain;box-shadow:0 10px 50px rgba(0,0,0,.6)}' +
    "#tp-lb .tp-lbcap{color:" + PAL.cream + ";font-family:'DM Mono',monospace;font-size:12px;letter-spacing:.5px;margin-top:14px;text-align:center;max-width:92vw}" +
    '#tp-lb .tp-lbcap a{color:' + PAL.ochre + ';text-decoration:none}' +
    '#tp-lb .tp-x{position:fixed;top:18px;right:22px;background:none;border:0;color:' + PAL.cream + ';font-size:34px;line-height:1;cursor:pointer}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // ── lightbox ──
  var lb = document.createElement('div');
  lb.id = 'tp-lb';
  lb.innerHTML = '<button class="tp-x" aria-label="Close">&times;</button><img alt=""><div class="tp-lbcap"></div>';
  var lbImg = lb.querySelector('img'), lbCap = lb.querySelector('.tp-lbcap');
  function openLb(p) {
    lbImg.src = wthumb(p.url, 1600);
    lbCap.innerHTML = esc(p.place) + ' — ' + esc(p.credit || 'Wikimedia Commons') +
      (p.license ? ' · ' + esc(p.license) : '') +
      (p.pageLink ? ' · <a href="' + p.pageLink + '" target="_blank" rel="noopener">source</a>' : '');
    lb.classList.add('open');
  }
  function closeLb() { lb.classList.remove('open'); lbImg.src = ''; }
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.className === 'tp-x') closeLb(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeLb(); });

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // attach an <img> with responsive src + graceful fallback chain
  function loadImg(img, p, width) {
    if (cache.failed[p.url]) { return false; }
    var stage = 0;
    var srcs = [p.url];
    img.loading = 'lazy'; img.decoding = 'async'; img.alt = p.place || '';
    img.onerror = function () {
      stage++;
      if (stage < srcs.length) { img.src = srcs[stage]; return; }
      cache.failed[p.url] = 1; persist();
      var fig = img.closest('.tp-shot') || img.closest('.tp-hero');
      if (fig) fig.style.display = 'none';
    };
    img.src = srcs[0];
    return true;
  }

  // ── hero ──
  if (data.hero && !cache.failed[data.hero.url]) {
    var hero = document.createElement('figure');
    hero.className = 'tp-hero';
    var hImg = document.createElement('img');
    loadImg(hImg, data.hero, 1600);
    hero.appendChild(hImg);
    var cap = document.createElement('figcaption');
    cap.className = 'tp-cap';
    cap.innerHTML = esc(data.hero.place) + ' · ' + esc(data.hero.credit || 'Wikimedia') +
      (data.hero.pageLink ? ' · <a href="' + data.hero.pageLink + '" target="_blank" rel="noopener">' + esc(data.hero.license || 'source') + '</a>' : '');
    hero.appendChild(cap);
    var mh = document.querySelector('.masthead');
    var root = document.getElementById('root');
    if (mh && mh.parentNode) mh.parentNode.insertBefore(hero, mh.nextSibling);
    else if (root && root.parentNode) root.parentNode.insertBefore(hero, root);
    else document.body.insertBefore(hero, document.body.firstChild);
  }

  // ── gallery ──
  var items = (data.items || []).filter(function (p) { return p && p.url && !cache.failed[p.url]; });
  if (items.length) {
    var g = document.createElement('section');
    g.className = 'tp-gallery';
    var head = document.createElement('div');
    head.innerHTML = '<div class="tp-lbl">— In pictures</div>' +
      '<h2 class="tp-ttl">The real <em>places</em></h2>';
    g.appendChild(head);
    var grid = document.createElement('div');
    grid.className = 'tp-grid';
    items.forEach(function (p) {
      var fig = document.createElement('figure');
      fig.className = 'tp-shot';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.setAttribute('aria-label', 'Enlarge photo of ' + (p.place || ''));
      var im = document.createElement('img');
      loadImg(im, p, 700);
      btn.appendChild(im);
      btn.addEventListener('click', function () { openLb(p); });
      fig.appendChild(btn);
      var fc = document.createElement('figcaption');
      fc.innerHTML = '<div class="tp-place">' + esc(p.place) + '</div>' +
        '<div class="tp-cred">' + esc(p.credit || 'Wikimedia Commons') +
        (p.pageLink ? ' · <a href="' + p.pageLink + '" target="_blank" rel="noopener">' + esc(p.license || 'source') + '</a>' : '') +
        '</div>';
      fig.appendChild(fc);
      grid.appendChild(fig);
    });
    g.appendChild(grid);

    var footer = document.querySelector('footer');
    var main = document.querySelector('main');
    var root2 = document.getElementById('root');
    if (footer && footer.parentNode) footer.parentNode.insertBefore(g, footer);
    else if (main) main.appendChild(g);
    else if (root2 && root2.parentNode) root2.parentNode.insertBefore(g, root2.nextSibling);
    else document.body.appendChild(g);
  }

  document.body.appendChild(lb);
})();
