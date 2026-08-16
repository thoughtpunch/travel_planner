// One-time seeder: writes the full 248-row activities catalog into the DB sheet.
// Run locally AFTER the service-account key exists:
//   GOOGLE_SA="$(cat sa-key.json)" SHEET_ID=1R5X... node tools/seed-sheet.mjs path/to/activities-seed.csv
import fs from 'node:fs';
import crypto from 'node:crypto';

const csvPath = process.argv[2];
if (!csvPath) { console.error('usage: node tools/seed-sheet.mjs <seed.csv>'); process.exit(1); }
const SHEET_ID = process.env.SHEET_ID;
const sa = JSON.parse(process.env.GOOGLE_SA);

function b64url(b){ return Buffer.from(b).toString('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_'); }
async function token(){
  const now = Math.floor(Date.now()/1000);
  const h = b64url(JSON.stringify({alg:'RS256',typ:'JWT'}));
  const c = b64url(JSON.stringify({iss:sa.client_email,scope:'https://www.googleapis.com/auth/spreadsheets',aud:'https://oauth2.googleapis.com/token',iat:now,exp:now+3600}));
  const s = crypto.createSign('RSA-SHA256'); s.update(h+'.'+c); s.end();
  const jwt = h+'.'+c+'.'+b64url(s.sign(sa.private_key));
  const r = await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({grant_type:'urn:ietf:params:oauth:grant-type:jwt-bearer',assertion:jwt})});
  const j = await r.json(); if(!j.access_token) throw new Error(JSON.stringify(j)); return j.access_token;
}
// minimal CSV parser (quoted fields, commas, doubled quotes)
function parseCSV(t){
  const rows=[]; let row=[], f='', q=false;
  for(let i=0;i<t.length;i++){ const ch=t[i];
    if(q){ if(ch==='"'){ if(t[i+1]==='"'){f+='"';i++;} else q=false; } else f+=ch; }
    else { if(ch==='"')q=true; else if(ch===','){row.push(f);f='';} else if(ch==='\n'){row.push(f);rows.push(row);row=[];f='';} else if(ch==='\r'){} else f+=ch; }
  }
  if(f.length||row.length){ row.push(f); rows.push(row); }
  return rows.filter(r=>r.length>1 || (r[0]&&r[0].length));
}
const values = parseCSV(fs.readFileSync(csvPath,'utf8'));
const tk = await token();
async function api(path,opts={}){ const r=await fetch('https://sheets.googleapis.com/v4/spreadsheets/'+path,{...opts,headers:{Authorization:'Bearer '+tk,'Content-Type':'application/json',...(opts.headers||{})}}); const t=await r.text(); if(!r.ok) throw new Error(r.status+': '+t); return t?JSON.parse(t):{}; }
const meta = await api(SHEET_ID+'?fields=sheets.properties.title');
const tab = meta.sheets[0].properties.title;
await api(SHEET_ID+'/values/'+encodeURIComponent(tab)+':clear',{method:'POST',body:'{}'});
await api(SHEET_ID+'/values/'+encodeURIComponent(tab)+'!A1?valueInputOption=RAW',{method:'PUT',body:JSON.stringify({values})});
console.log('seeded', values.length-1, 'rows into tab', JSON.stringify(tab));
