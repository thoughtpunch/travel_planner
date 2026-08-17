import fs from 'fs';
const EXT = '/private/tmp/claude-501/-Users-dan-sites-thoughtpunch-trip-planner/7707d7f7-2985-4375-89db-d68e117081d9/scratchpad/ext/';
const OUT = '/Users/dan/sites/thoughtpunch/trip_planner/italy-trip-2026/public/';

// ── load curated (array) via sandboxed eval ──
const window = {};
eval(fs.readFileSync(EXT + 'curated.js', 'utf8'));
const LEGS = window.TRIP_LEGS;
const curated = window.TRIP_ADVENTURES.map(x => ({ ...x, _src: 'cur' }));
const legCity = {}; LEGS.forEach(l => legCity[l.leg] = l.city);
const legRg = {}; LEGS.forEach(l => legRg[l.leg] = l.rg);

// ── per-file defaults ──
const FILES = [
  ['milan.json', 1, 'Lombardy'], ['turin.json', 2, 'Piedmont'],
  ['cinqueterre.json', 3, 'Liguria'], ['florence.json', 4, 'Tuscany'],
  ['rome.json', 5, 'Lazio'], ['venice.json', 6, 'Veneto'],
  ['dolomites.json', 7, 'Trentino–Alto Adige'], ['bologna.json', 4, 'Emilia-Romagna'],
  ['romevenice.json', 6, 'Emilia-Romagna'], ['biking.json', 3, 'Liguria'],
  ['celebrations.json', 4, 'Italy'],
];

function dec(s){ return String(s==null?'':s)
  .replace(/&amp;/g,'&').replace(/&#0?39;/g,"'").replace(/&rsquo;|&lsquo;/g,"'")
  .replace(/&quot;/g,'"').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&nbsp;/g,' '); }

function normRg(r){ return /south tyrol|alto adige/i.test(r||'') ? 'Trentino–Alto Adige' : (r||''); }

function cleanLink(l){
  if (!l) return '';
  if (l.startsWith('/') || /\.html($|[?#])/i.test(l)) return '';
  return l;
}

const ext = [];
for (const [f, leg, rg] of FILES) {
  const arr = JSON.parse(fs.readFileSync(EXT + f, 'utf8'));
  for (const it of arr) {
    const L = it.leg || leg;
    ext.push({
      leg: L,
      city: it.city || legCity[L],
      rg: normRg(it.rg || rg || legRg[L]),
      n: dec(it.n), b: dec(it.b),
      w: it.w && it.w.length ? it.w : ['all'],
      g: dec(it.g), k: dec(it.k),
      c: it.c || 'sight', r: it.r || 'base',
      s: !!it.s, l: cleanLink(it.l), img: '',
      _src: 'ext',
    });
  }
}
// normalize curated too
for (const it of curated){ it.n=dec(it.n); it.b=dec(it.b); it.g=dec(it.g||''); it.k=dec(it.k||''); it.rg=normRg(it.rg); it.l=cleanLink(it.l); it.img=it.img||''; it.w=it.w&&it.w.length?it.w:['all']; }

// curated FIRST so it becomes the merge base (keeps its photos/links/framing)
const combined = [...curated, ...ext];

// ── dedup: same leg + >=2 shared significant title tokens ──
const STOP = new Set(['with','your','into','from','over','near','plus','tour','trip','walk','best','little','they','them','this','that','then','make','made','onto','the','and','for']);
function toks(n){
  return new Set(dec(n).toLowerCase().replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(t => t.length>=4 && !STOP.has(t)));
}
function shared(a,b){ let n=0; for (const t of a) if (b.has(t)) n++; return n; }
function longest(w){ return w.filter(Boolean).sort((x,y)=>y.length-x.length)[0]||''; }

const accepted = [];
for (const it of combined){
  const T = toks(it.n);
  let hit = null;
  for (const a of accepted){ if (a.leg===it.leg && shared(a._T, T)>=2){ hit=a; break; } }
  if (hit){
    if ((it.b||'').length > (hit.b||'').length) hit.b = it.b;
    for (const w of it.w) if (!hit.w.includes(w)) hit.w.push(w);
    hit.s = hit.s || it.s;
    if (!hit.g && it.g) hit.g = it.g;
    if (!hit.k && it.k) hit.k = it.k;
    if (!hit.l && it.l) hit.l = it.l;
    if (!hit.img && it.img) hit.img = it.img;
    if (!hit.city && it.city) hit.city = it.city;
  } else {
    it._T = T; accepted.push(it);
  }
}

// ── targeted force-merges (true dups the token rule missed) ──
const FORCE = [
  [1,/leonardo science museum/i,/museo nazionale scienza/i],
  [2,/superga rack railway/i,/superga by the old cog/i],
  [3,/portovenere & the byron/i,/portovenere and the gulf/i],
  [4,/la specola — minerals/i,/la specola natural/i],
  [3,/make pesto by hand/i,/^pesto-making class/i],
];
for (const [leg, keepRe, dropRe] of FORCE){
  const keep = accepted.find(x=>x.leg===leg && keepRe.test(x.n));
  const di = accepted.findIndex(x=>x.leg===leg && dropRe.test(x.n));
  if (keep && di>=0 && accepted[di]!==keep){
    const d = accepted[di];
    if ((d.b||'').length>(keep.b||'').length) keep.b=d.b;
    for (const w of d.w) if(!keep.w.includes(w)) keep.w.push(w);
    keep.s = keep.s||d.s; if(!keep.g&&d.g)keep.g=d.g; if(!keep.k&&d.k)keep.k=d.k;
    if(!keep.l&&d.l)keep.l=d.l; if(!keep.img&&d.img)keep.img=d.img;
    accepted.splice(di,1);
  }
}

// ── re-attach headliner photos by leg-scoped rule ──
const PH = 'https://commons.wikimedia.org/wiki/Special:FilePath/';
const PHOTO_RULES = [
  [1,/toti|leonardo da vinci|scienza e tecnologia/i,'Nave_sottomarino_-_Museo_scienza_tecnologia_Milano_09676.jpg'],
  [1,/storia naturale/i,'Veduta_del_Museo_civico_di_storia_naturale_di_Milano.jpg'],
  [1,/duomo \+ rooftop|duomo terraces/i,'Milan_Cathedral_from_Piazza_del_Duomo.jpg'],
  [2,/novara|san gaudenzio/i,'Novara_Basilica_di_San_Gaudenzio_Esterno_Cupola_1.jpg'],
  [2,/mole antonelliana|cinema museum/i,'Mole_Antonelliana_Torino.JPG'],
  [2,/museo egizio|egyptian museum/i,'Statua_Sekhmet_Museo_Egizio_Torino_Maggio_2025.jpg'],
  [2,/sotterranea|pietro micca/i,'Pietro_Micca_death_place.jpg'],
  [3,/nazario sauro|galata|submarine/i,'Nazario_Sauro_(S_518).jpg'],
  [3,/portovenere/i,'Portovenere_harbour_and_Doria_Castle,_Liguria,_Italy,_April_2026.jpg'],
  [3,/monterosso/i,'Monterosso_al_Mare-panorama-Fegina1.jpg'],
  [4,/carrara/i,'Carrara_marble_quarry_face.jpg'],
  [4,/pietrasanta/i,'Piazza_Duomo_(Pietrasanta).jpg'],
  [4,/scuola del cuoio|leather school/i,'Scuola_del_cuoio_Firenze.jpg'],
  [4,/la specola/i,'Universit%C3%A0_di_Firenze_Museo_Zoologico_%22La_Specola%22_(89368).jpg'],
  [4,/palazzo vecchio/i,'Palazzo_vecchio_Florence.jpg'],
  [4,/brunelleschi|climb the dome|cupola/i,'Cupola_di_santa_maria_del_fiore_dal_campanile_di_giotto,_01.JPG'],
  [4,/masone|bamboo/i,'Il_Labirinto_della_Masone_visto_dallalto,_Labirinto_della_Masone,_Fontanellato_(PR),_Italia,_2019_foto_G.Ferretti.jpg'],
  [5,/orvieto|san patrizio/i,'Pozzo_di_San_Patrizio,_Orvieto.jpg'],
  [5,/colosseum underground|hypogeum/i,'Hypogeum_1_(15005526662).jpg'],
  [5,/capuchin|bone chapel/i,'Capuchin_Crypt_-_DPLA_-_103cc5af0b9e4d62334af9db890b7c8b.jpg'],
  [5,/copped/i,'Palace_in_quartiere_copped%C3%A8.jpg'],
  [5,/castel sant/i,'RomaCastelSantAngelo.jpg'],
  [5,/bomarzo|park of the monsters/i,'Monster_in_Parco_dei_Mostri_(Bomarzo).jpg'],
  [6,/murano/i,'Murano_furnace_and_pipe.jpg'],
  [6,/doge/i,'Doge%27s_Palace_Venice_sea_facade.jpg'],
  [6,/arsenal/i,'Arsenale_di_Venezia_gate.jpg'],
  [6,/villa pisani/i,'Labirinto_villa_Pisani_1.JPG'],
  [7,/seceda/i,'The_Dolomites_from_Seceda.jpg'],
  [7,/alpe di siusi|seiser/i,'Gr%C3%B6dner_Dolomiten_Seiser-Alm_Hi_res.jpg'],
  [7,/bletterbach/i,'Bletterbach_HDR.jpg'],
  [7,/sassolungo|coffin/i,'Langkofel_group_from_the_Sella_pass_2016.jpg'],
];
for (const it of accepted){
  for (const [leg, re, file] of PHOTO_RULES){
    if (it.leg===leg && re.test(it.n)){ it.img = PH + file + '?width=800'; break; }
  }
}

// ── city-level fallback image so EVERY row has a picture ──
let CITY_IMG = {};
try { CITY_IMG = JSON.parse(fs.readFileSync(EXT + 'city-images.json', 'utf8')); } catch (e) { console.log('(no city-images.json yet)'); }
for (const it of accepted) {
  if (!it.img) it.img = CITY_IMG[it.city] || CITY_IMG[legCity[it.leg]] || '';
}

// ── sort: leg, then reach (way,base,far), then title ──
const RO = { way:0, base:1, day:2, far:3 };
accepted.sort((a,b)=> a.leg-b.leg || (RO[a.r]-RO[b.r]) || a.n.localeCompare(b.n));

// ── emit adventures-data.js ──
function ser(it){
  const p = [`leg:${it.leg}`, `city:${JSON.stringify(it.city)}`, `rg:${JSON.stringify(it.rg)}`,
    `n:${JSON.stringify(it.n)}`, `b:${JSON.stringify(it.b)}`, `w:${JSON.stringify(it.w)}`];
  if (it.g) p.push(`g:${JSON.stringify(it.g)}`);
  if (it.k) p.push(`k:${JSON.stringify(it.k)}`);
  p.push(`c:${JSON.stringify(it.c)}`, `r:${JSON.stringify(it.r)}`);
  if (it.s) p.push('s:true');
  if (it.l) p.push(`l:${JSON.stringify(it.l)}`);
  if (it.img) p.push(`img:${JSON.stringify(it.img)}`);
  return `  { ${p.join(', ')} },`;
}
const header = `/* ============================================================================
 * adventures-data.js — the single DB of every non-stay location on the trip
 * Auto-generated (dedup + enrich + format) from all city/celebration pages.
 * Rendered by adventures.html into the sortable/filterable reference table.
 * Fields: leg, city, rg(region), n(title), b(desc), w(ideal-for), g(get there),
 *         k(cost), c(category), r(reach base|way|day|far), s(★), l(site), img.
 * ==========================================================================*/
window.TRIP_LEGS = ${JSON.stringify(LEGS, null, 0).replace(/},/g,' },\n  ').replace(/^\[/,'[\n  ').replace(/\]$/,'\n]')};

window.TRIP_ADVENTURES = [
${accepted.map(ser).join('\n')}
];
`;
fs.writeFileSync(OUT + 'adventures-data.js', header);

// ── emit adventures.csv ──
function q(s){ s=String(s==null?'':s); return '"'+s.replace(/"/g,'""')+'"'; }
function maps(it){ return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(it.n+' '+it.city+' Italy'); }
const REACHL = { base:'In town', way:'On the way', day:'Day-trip', far:'Far · own trip' };
const rows = [['Leg','City','Region','Title','Description','Ideal for','How to get there','Cost','Category','Reach','Adventure','Website','Google Maps','Photo']];
for (const it of accepted){
  rows.push([it.leg, it.city, it.rg, it.n, it.b, it.w.join(' · '), it.g, it.k||'', it.c, REACHL[it.r]||it.r, it.s?'★':'', it.l||'', maps(it), it.img||'']);
}
fs.writeFileSync(OUT + 'adventures.csv', rows.map(r=>r.map(q).join(',')).join('\n')+'\n');

// ── stats ──
const byLeg = {}; accepted.forEach(a=>byLeg[a.leg]=(byLeg[a.leg]||0)+1);
const withPhoto = accepted.filter(a=>a.img).length;
console.log('IN combined:', combined.length, '→ OUT deduped:', accepted.length, '| photos:', withPhoto);
console.log('per leg:', byLeg);
