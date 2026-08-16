import fs from 'fs';
const window={}; eval(fs.readFileSync('./public/adventures-data.js','utf8'));
const A=window.TRIP_ADVENTURES;
const slug=(leg,n)=> leg+'-'+n.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,60);
const q=s=>'"'+String(s==null?'':s).replace(/"/g,'""')+'"';
const rows=[['id','leg','city','region','title','ideal_for','category','reach','cost','how_to_get_there','website','status','notes','updated']];
for(const it of A){
  rows.push([slug(it.leg,it.n),it.leg,it.city,it.rg,it.n,(it.w||[]).join(' · '),it.c,it.r,it.k||'',it.g||'',it.l||'','','','']);
}
fs.writeFileSync('/private/tmp/claude-501/-Users-dan-sites-thoughtpunch-trip-planner/7707d7f7-2985-4375-89db-d68e117081d9/scratchpad/activities-seed.csv', rows.map(r=>r.map(q).join(',')).join('\n')+'\n');
console.log('seed rows:',rows.length-1);
