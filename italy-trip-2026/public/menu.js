/* Global hamburger menu — injected on every page (React home + all static pages)
   so you can reach any stop/section from anywhere. Self-contained, no deps. */
(function () {
  var GROUPS = [
    {
      title: 'The loop',
      links: [
        { label: 'Home · the map', href: '/' },
        { label: '1 · Rome', href: '/rome' },
        { label: '2 · Naples', href: '/naples' },
        { label: '3 · Sicily', href: '/sicily' },
        { label: '4 · Bologna + Florence', href: '/bologna' },
        { label: '5 · Dolomites (Bolzano)', href: '/bolzano' },
        { label: '6 · Venice / Lido', href: '/venice' },
        { label: '7 · Croatia', href: '/croatia' },
      ],
    },
    {
      title: 'Activities by kid',
      links: [
        { label: 'Rhys · 18', href: '/rhys' },
        { label: 'Jude · 16', href: '/jude' },
        { label: 'Grey · 12', href: '/grey' },
        { label: 'Keir · 9', href: '/keir' },
      ],
    },
    {
      title: 'More',
      links: [
        { label: 'Activities hub', href: '/activities' },
        { label: 'Boy adventures', href: '/adventures' },
        { label: 'Worldschooling families', href: '/worldschooling' },
        { label: 'The full plan', href: '/plan' },
      ],
    },
  ]

  function norm(p) {
    if (!p) return '/'
    p = p.replace(/\.html$/, '').replace(/\/index$/, '/')
    if (p.length > 1 && p.charAt(p.length - 1) === '/') p = p.slice(0, -1)
    return p === '' ? '/' : p
  }
  var here = norm(location.pathname)

  var css =
    '#nav-fab{position:fixed;top:16px;right:16px;z-index:10001;display:flex;align-items:center;gap:8px;' +
    'background:#1A1510;color:#F5F0E8;border:1px solid #C4531A;border-radius:3px;padding:9px 13px;cursor:pointer;' +
    "font-family:'DM Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;box-shadow:0 2px 10px rgba(0,0,0,.3)}" +
    '#nav-fab:hover{color:#D4920A;border-color:#D4920A}' +
    '#nav-fab .bars{display:inline-block;width:16px;height:11px;position:relative}' +
    '#nav-fab .bars span{position:absolute;left:0;width:100%;height:2px;background:currentColor}' +
    '#nav-fab .bars span:nth-child(1){top:0}#nav-fab .bars span:nth-child(2){top:4.5px}#nav-fab .bars span:nth-child(3){top:9px}' +
    '#nav-backdrop{position:fixed;inset:0;background:rgba(26,21,16,.55);z-index:10002;opacity:0;pointer-events:none;transition:opacity .2s}' +
    '#nav-backdrop.open{opacity:1;pointer-events:auto}' +
    '#nav-panel{position:fixed;top:0;right:0;height:100%;width:320px;max-width:86vw;background:#1A1510;color:#F5F0E8;z-index:10003;' +
    'transform:translateX(100%);transition:transform .25s ease;overflow-y:auto;padding:22px 26px 40px;box-shadow:-6px 0 30px rgba(0,0,0,.4)}' +
    '#nav-panel.open{transform:translateX(0)}' +
    '#nav-panel .nav-x{position:absolute;top:16px;right:18px;background:none;border:none;color:#8C7B6B;font-size:26px;line-height:1;cursor:pointer}' +
    '#nav-panel .nav-x:hover{color:#D4920A}' +
    "#nav-panel .nav-brand{font-family:'Playfair Display',serif;font-weight:900;font-size:22px;margin:2px 0 18px}" +
    "#nav-panel .nav-brand em{font-style:italic;color:#D4920A;font-weight:400}" +
    "#nav-panel h4{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#8C7B6B;margin:22px 0 8px;border-bottom:1px solid rgba(196,185,168,.18);padding-bottom:6px}" +
    '#nav-panel a{display:block;color:#F5F0E8;padding:7px 0;font-size:15px;border-bottom:1px solid rgba(196,185,168,.08)}' +
    '#nav-panel a:hover{color:#D4920A}' +
    '#nav-panel a.cur{color:#C4531A;font-weight:500}' +
    '#nav-panel a.cur:before{content:"\\2192 ";color:#C4531A}'

  var style = document.createElement('style')
  style.textContent = css
  document.head.appendChild(style)

  var fab = document.createElement('button')
  fab.id = 'nav-fab'
  fab.setAttribute('aria-label', 'Open menu')
  fab.innerHTML = '<span class="bars"><span></span><span></span><span></span></span>Menu'

  var backdrop = document.createElement('div')
  backdrop.id = 'nav-backdrop'

  var panel = document.createElement('nav')
  panel.id = 'nav-panel'
  panel.setAttribute('aria-label', 'Site navigation')

  var html = '<button class="nav-x" aria-label="Close menu">&times;</button>' +
    '<div class="nav-brand">Italy <em>2026</em></div>'
  GROUPS.forEach(function (g) {
    html += '<h4>' + g.title + '</h4>'
    g.links.forEach(function (l) {
      var cur = norm(l.href) === here ? ' class="cur"' : ''
      html += '<a href="' + l.href + '"' + cur + '>' + l.label + '</a>'
    })
  })
  panel.innerHTML = html

  document.body.appendChild(fab)
  document.body.appendChild(backdrop)
  document.body.appendChild(panel)

  function open() { panel.classList.add('open'); backdrop.classList.add('open') }
  function close() { panel.classList.remove('open'); backdrop.classList.remove('open') }
  fab.addEventListener('click', open)
  backdrop.addEventListener('click', close)
  panel.querySelector('.nav-x').addEventListener('click', close)
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close() })
})()
