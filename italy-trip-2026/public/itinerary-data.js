/* ============================================================================
 * itinerary-data.js — the day-by-day master. ONE entry per day, Sep 9 → Oct 15.
 * ----------------------------------------------------------------------------
 * This is the operational document: exact times, every booked bed, every ticket,
 * every hard deadline. If it isn't in here it doesn't happen.
 *
 * Each day:  { d:'2026-09-13', city:'Milan → Turin', note:'…',
 *              items:[ { t:'11:15', k:<kind>, s:<status>, w:'what', d:'detail' } ] }
 *
 *   kind   travel | stay | eat | do | admin | milestone
 *   status booked   — paid/confirmed, nothing to do
 *          tobook   — MUST be booked, usually with a deadline
 *          plan     — intended, no booking needed
 *          free     — costs nothing
 * Times are LOCAL to where they happen. Days with no fixed time use t:''.
 * ==========================================================================*/
window.ITINERARY = [
{ d:'2026-09-09', wd:'Wed', city:'San José → Washington', leg:0, note:'Travel day one. Nothing in Italy yet.', items:[
  { t:'19:45', k:'travel', s:'booked', w:'SJO → IAD · Avianca AABDA8', d:'1 stop · 6h35 · arrives Dulles 04:20 +1. Light fare: 1 carry-on each, 0 checked.' },
]},
{ d:'2026-09-10', wd:'Thu', city:'Washington → Keflavík', leg:0, note:'The 19-hour cushion between two unconnected tickets. Do not book anything rigid.', items:[
  { t:'04:20', k:'travel', s:'booked', w:'Land IAD — clear US immigration', d:'Six passports in the small hours. Queues are thin at that time.' },
  { t:'~06:00', k:'travel', s:'plan', w:'IAD → BWI by road, ~1 hour', d:'Self-transfer, neither airline involved. Amy is 4 miles from Dulles if you want the gap hours somewhere comfortable.' },
  { t:'23:20', k:'travel', s:'booked', w:'BWI → KEF · Icelandair FI640', d:'5h50 · arrives Keflavík 09:10. Ref AMBVO4.' },
]},
{ d:'2026-09-11', wd:'Fri', city:'→ MILAN', leg:1, note:'Day three of travelling. Everyone will be wrecked — the plan is deliberately empty.', items:[
  { t:'15:45', k:'travel', s:'booked', w:'KEF → MXP · Icelandair FI592', d:'After a 6h35 layover. Lands Malpensa Terminal 1 at 21:55.' },
  { t:'21:55', k:'travel', s:'booked', w:'LAND MILAN MALPENSA T1', d:'Schengen entry cleared here. 34 nights in Italy start now.' },
  { t:'~22:56', k:'travel', s:'tobook', w:'Malpensa Express T1 → Milano Cadorna', d:'Buy at the T1 machine — fixed price, no advance booking. ASK FOR THE FAMILY TICKET: €36 covers 2 adults + 2 children 4–17, then €15 each for the other two. ~€66. Trains every ~30 min, last one 00:26.' },
  { t:'~23:40', k:'travel', s:'plan', w:'Cadorna → Coni Zugna · tram 2', d:'13 min, then 89 m to the door. ATM tickets €2.20 × 4 payers, Grey and Keir free. If the wait looks grim, the Cadorna taxi rank is right outside — two cars ~€25–30.' },
  { t:'~00:15', k:'stay', s:'booked', w:'CHECK IN — Milano Chic Retreat', d:'Via Antonio Dugnani 1, 20144 Milano. Elevator. 2 bedrooms (2 queens) + sofa bed, 2 baths. $606.05 paid.' },
]},
{ d:'2026-09-12', wd:'Sat', city:'MILAN', leg:1, note:'The one day in Milan, and the reason the flat is where it is.', items:[
  { t:'', k:'do', s:'plan', w:'★ Leonardo Science Museum + the Toti submarine', d:'Via San Vittore 21 — a 600 m / 9-min walk from the door. Under-18s free, adults ~€10. Italy’s biggest science museum: Leonardo machine models, steam trains, and a walk-through submarine.' },
  { t:'', k:'do', s:'free', w:'Anything else is a bonus', d:'Free and nearby if there is energy: Cimitero Monumentale, San Bernardino alle Ossa bone chapel, the Galleria bull-heel spin. Do not overload day one.' },
]},
{ d:'2026-09-13', wd:'Sun', city:'MILAN → TURIN', leg:2, note:'First train. Everything is booked and seated.', items:[
  { t:'~10:30', k:'stay', s:'plan', w:'CHECK OUT — Via Dugnani', d:'' },
  { t:'10:35', k:'travel', s:'plan', w:'Leave the flat', d:'400 m to Sant’Agostino (M2) → 5 stops to Garibaldi FS → 3 min into the station. ~20 min total.' },
  { t:'11:15', k:'travel', s:'booked', w:'★ FRECCIAROSSA 9304 · Milano Porta Garibaldi → Torino', d:'PNR NY2TU5 · €83.60 · Coach 8: Dan 7D, Rhys 7C, Grey 7B, Kei 8D, Jude 8C, Keir 8B. Doors close 11:14. NOT Centrale — it has no direct Turin trains this morning.' },
  { t:'12:20', k:'travel', s:'plan', w:'ARRIVE AT TORINO PORTA NUOVA', d:'Stay aboard to the final stop. The flat on Via San Massimo is about 1.1 km away; take a short taxi with the luggage.' },
  { t:'~12:30', k:'stay', s:'booked', w:'CHECK IN — "Mole" House, Turin', d:'Via San Massimo 9, 10123 Torino. 2BR/1 bath. $415.71 paid. Reservation HMMSR2JEC5.' },
]},
{ d:'2026-09-14', wd:'Mon', city:'TURIN', leg:2, note:'One full day in Turin.', items:[
  { t:'', k:'do', s:'plan', w:'Museo Egizio', d:'World’s second-best Egyptian collection. €18 adult, €1 for ages 6–14, €3 for 15–18 — Rhys is still 17, so this is cheap: ~€44 for six. Family ticket €36 for 2 adults + 2 minors is worth asking about.' },
  { t:'', k:'do', s:'plan', w:'Mole Antonelliana + Cinema Museum', d:'The glass lift up the middle of the dome. Or skip the museum and just do the lift.' },
]},
{ d:'2026-09-15', wd:'Tue', city:'TURIN → DAMANHUR → LIGURIAN COAST', leg:3, note:'Damanhur Classic Visit selected. FR 8623 still needs booking.', items:[
  { t:'07:45', k:'stay', s:'plan', w:'CHECK OUT — Turin', d:'Take all luggage in the pre-booked NCC to Vidracco. Host Marcello +39 333 822 7352.' },
  { t:'15:15', k:'travel', s:'tobook', w:'Torino Porta Nuova → Chiavari · Frecciarossa 8623', d:'Replacement after Damanhur; arrives 17:44. Book for six. The cancelled Intercity 511 used PNRs N7PZ5N / N7MGC5; the €31.20 Bimbi Gratis refund is recorded in the rail ledger.' },
  { t:'~18:00', k:'stay', s:'booked', w:'CHECK IN — Vista sul Carruggio, Chiavari', d:'Via Vittorio Veneto 16, INTERNO 1, PIANO 1, 16043 Chiavari GE. €506.54 paid. Station is 600 m / 8 min. Piano 1 = first floor; lift NOT confirmed.' },
]},
{ d:'2026-09-16', wd:'Wed', city:'LIGURIAN COAST', leg:3, note:'', items:[
  { t:'', k:'do', s:'plan', w:'Cinque Terre by train', d:'Chiavari sits OUTSIDE the Cinque Terre card zone. Buy Chiavari→Levanto as a normal regional (~€26 for six), then decide on the park card separately.' },
]},
{ d:'2026-09-17', wd:'Thu', city:'LIGURIAN COAST', leg:3, note:'', items:[
  { t:'', k:'do', s:'plan', w:'★ Genoa — walk through a real submarine', d:'Galata Museo del Mare + the Nazario Sauro. €19 full / €14 ages 7–17, family €42. ~€94 for six. On the shortlist.' },
]},
{ d:'2026-09-18', wd:'Fri', city:'LIGURIAN COAST', leg:3, note:'RHYS TURNS 18.', items:[
  { t:'', k:'milestone', s:'plan', w:'🎂 Rhys turns 18', d:'From today he pays FULL adult at every Italian state museum — the €2 EU reduced rate is not open to Americans. Anything state-run you wanted him free at had to happen before today.' },
  { t:'', k:'eat', s:'tobook', w:'Rhys’s birthday dinner — seafood over the Mediterranean', d:'And his first legal drink. Worth reserving ahead.' },
]},
{ d:'2026-09-19', wd:'Sat', city:'COAST → FLORENCE', leg:4, note:'Train BOOKED. PARTY OF 7 — Grandma came for Rhys’s 18th (one night in Chiavari) and rides to Florence with us.', items:[
  { t:'~10:00', k:'stay', s:'plan', w:'CHECK OUT — Chiavari', d:'' },
  { t:'09:31', k:'travel', s:'booked', w:'Chiavari → Firenze S.M.N. · Intercity 505, change at Pisa', d:'Pisa Centrale 11:07, ⚠️ 23-min change, RV 4030 at 11:30, arrives 12:33. PARTY OF 7. Coach 4 — Dan 18A, Kei 18B, Grey 19A, Keir 19B (PNR N7SKJN, €51.00); Rhys 18C, Jude 18D, Nancy 19C (PNR N7S4TN, €61.80). ⚠️ Seats cover the Pisa leg only — the Florence train is a Regionale, open seating. Leave the flat 09:10.' },
  { t:'~15:30', k:'stay', s:'booked', w:'CHECK IN — San Frediano, Florence', d:'Via dell’Orto, 50124 Firenze. 7 nights. $1,937.57 paid. NON-REFUNDABLE. Tassa di soggiorno included.' },
  { t:'', k:'milestone', s:'plan', w:'Grandma arrives — 7 people this week', d:'Budget ~$250–350 extra for the week if she isn’t covering her own meals.' },
]},
{ d:'2026-09-20', wd:'Sun', city:'FLORENCE', leg:4, note:'', items:[
  { t:'', k:'do', s:'plan', w:'Uffizi', d:'€29 online / €25 door in September (peak). Under-18s FREE any nationality — so only Dan, Kei and Rhys pay. ~€87.' },
]},
{ d:'2026-09-21', wd:'Mon', city:'FLORENCE', leg:4, note:'Dan works 4–11pm Mon–Fri from here.', items:[
  { t:'', k:'do', s:'free', w:'San Miniato al Monte', d:'Free, the best view in Florence, Gregorian chant at vespers most afternoons. Better than Piazzale Michelangelo just below it.' },
]},
{ d:'2026-09-22', wd:'Tue', city:'FLORENCE', leg:4, note:'', items:[
  { t:'', k:'do', s:'tobook', w:'★ Pizza + gelato from scratch (Florencetown)', d:'€354 for six. On the shortlist. Book ahead.' },
]},
{ d:'2026-09-23', wd:'Wed', city:'FLORENCE', leg:4, note:'', items:[
  { t:'', k:'do', s:'plan', w:'Bologna food day-trip', d:'37 min by Frecciarossa each way. ⚠️ Torre degli Asinelli is CLOSED for all of 2026 — climb Torre dell’Orologio on Piazza Maggiore instead (~€8pp).' },
]},
{ d:'2026-09-24', wd:'Thu', city:'FLORENCE', leg:4, note:'Rest day. Markets, Oltrarno, nothing scheduled.', items:[]},
{ d:'2026-09-25', wd:'Fri', city:'FLORENCE', leg:4, note:'', items:[
  { t:'19:00', k:'do', s:'tobook', w:'Vasari Corridor — Friday night opening', d:'€24pp advance, ~€107 for six. Friday evenings 7–11pm through Nov 20. The Medici’s private passage above the Ponte Vecchio, at night. Cheapest special thing on the trip.' },
]},
{ d:'2026-09-26', wd:'Sat', city:'FLORENCE → ROME', leg:5, note:'Train BOOKED (PNR N7T7W5). Grandma leaves Florence.', items:[
  { t:'~10:00', k:'stay', s:'plan', w:'CHECK OUT — Florence', d:'Verified checkout deadline is 10:00. Take all luggage to Firenze S.M.N.' },
  { t:'~10:30', k:'admin', s:'plan', w:'DROP BAGS — KiPoint, Firenze S.M.N.', d:'Leave all luggage at the station KiPoint. Collect it by about 13:20 for the 13:48 Frecciarossa.' },
  { t:'13:48', k:'travel', s:'booked', w:'Firenze S.M.N. → Roma Termini · Frecciarossa 9415 · PNR N7T7W5', d:'Direct, 1h47, arrives 15:35. €50.00 + €55.80 split 4+2, FrecciaFAMILY applied. Coach 5 — Dan 15A, Kei 15B, Grey 16A, Keir 16B (PNR N7T7W5, €50.00, FrecciaFAMILY); Rhys 14A, Jude 14B (PNR N7UFZN, €55.80). Taxi from Termini (~€12–15) rather than Metro A — Re di Roma has stairs.' },
  { t:'16:00', k:'stay', s:'booked', w:'CHECK IN — Domus Flavii, Rome', d:'Via Appia Nuova 185, int 9, 00182 Roma — on Piazza Re di Roma, 150 m from Metro A. 7 nights. $2,285.24 — ⚠️ charges to PayPal on SEP 13, make sure that account is funded.' },
  { t:'', k:'eat', s:'plan', w:'Dan’s free evening #1', d:'Dan works 4–11pm Mon–Fri, so Sat 26 and Sun 27 are his ONLY free nights in Rome. Front-load anything after dark.' },
]},
{ d:'2026-09-27', wd:'Sun', city:'ROME', leg:5, note:'🎯 FREE VATICAN — last Sunday of the month.', items:[
  { t:'~07:30', k:'do', s:'free', w:'★ Vatican Museums + Sistine Chapel — FREE TODAY', d:'Last Sunday of every month. Saves ~€90–120. No advance booking, big queues, shortened hours (reported 09:00–14:00, last entry 12:30). Arrive before 08:00 or treat it as optional.' },
  { t:'evening', k:'eat', s:'plan', w:'Evening centro walk — Pantheon, Trevi, Navona', d:'Free, and Dan’s last free night for a week.' },
]},
{ d:'2026-09-28', wd:'Mon', city:'ROME', leg:5, note:'Dan works 4–11pm.', items:[
  { t:'', k:'do', s:'tobook', w:'★ Gladiator school — Scuola Gladiatori', d:'€690 for six, the trip’s single biggest activity. Age 6+, so Keir clears it. ⚠️ CALL FIRST — they note a discount for groups of 3+. Consider moving this to Oct 1–3 to shift $800 out of September.' },
]},
{ d:'2026-09-29', wd:'Tue', city:'ROME', leg:5, note:'', items:[
  { t:'', k:'do', s:'plan', w:'Colosseum + Forum + Palatine', d:'€18 each, no booking fee, under-18s FREE. So ~€54 for the three payers. Book the timed slot ahead.' },
]},
{ d:'2026-09-30', wd:'Wed', city:'ROME', leg:5, note:'', items:[
  { t:'', k:'do', s:'free', w:'Free Rome', d:'Caravaggios at San Luigi dei Francesi and Santa Maria del Popolo (bring €1 coins for the lights), Sant’Ignazio’s fake dome, the Aventine Keyhole.' },
]},
{ d:'2026-10-01', wd:'Thu', city:'ROME', leg:5, note:'', items:[
  { t:'', k:'do', s:'plan', w:'Domus Aurea + VR', d:'€156 for six. Nero’s buried palace with a VR reconstruction — the best-value big-ticket thing in Rome.' },
]},
{ d:'2026-10-02', wd:'Fri', city:'ROME', leg:5, note:'Rest day before the long Venice run.', items:[]},
{ d:'2026-10-03', wd:'Sat', city:'ROME → VENICE', leg:6, note:'⚠️ Train NOT booked, deadline Sep 18. Longest travel day.', items:[
  { t:'~10:00', k:'stay', s:'plan', w:'CHECK OUT — Rome', d:'' },
  { t:'11:35', k:'travel', s:'tobook', w:'Roma Termini → Venezia S. Lucia · Frecciarossa', d:'3h59 direct, arrives 15:34. ~€144–170 split 4+2 — the priciest leg. BOOK BY SEP 18; one departure already showed only 8 family seats left.' },
  { t:'~16:00', k:'travel', s:'tobook', w:'Buy 6 × 7-day ACTV vaporetto passes', d:'€65 each, €390 total. No child rate — everyone pays. Break-even is 3.5 round trips and you are based on the Lido, so this beats singles by ~€180.' },
  { t:'~16:30', k:'stay', s:'booked', w:'CHECK IN — Appartamento alle terrazze, Lido', d:'Next door to MuMu. 7 nights. $1,232.14 paid, ⚠️ balance $944.05 charges SEP 18.' },
]},
{ d:'2026-10-04', wd:'Sun', city:'VENICE / LIDO', leg:6, note:'🎯 FREE state museums — first Sunday of the month.', items:[
  { t:'09:00', k:'do', s:'free', w:'★ Gallerie dell’Accademia — FREE TODAY', d:'First-Sunday state scheme. Saves €60. Also free: Ca’ d’Oro, Museo Archeologico, Palazzo Grimani. Venice’s CIVIC museums (Doge’s, Correr) opt out. Go at opening — free Sunday means crowds.' },
]},
{ d:'2026-10-05', wd:'Mon', city:'VENICE / LIDO', leg:6, note:'Dan works 4–11pm. MuMu is the point of this week — build days around her.', items:[
  { t:'', k:'admin', s:'tobook', w:'Buy 4 × Rolling Venice cards, €6 each', d:'Ages 6–29, passport only. A named MUVE reduction category, and it drops the 72h vaporetto pass from €45 to €27. Sold at the Lido Venezia Unica point.' },
]},
{ d:'2026-10-06', wd:'Tue', city:'VENICE / LIDO', leg:6, note:'', items:[
  { t:'', k:'do', s:'tobook', w:'★ Murano — watch glassblowing, make a bead', d:'€270 for six. On the shortlist. Your vaporetto pass covers getting there.' },
]},
{ d:'2026-10-07', wd:'Wed', city:'VENICE / LIDO', leg:6, note:'', items:[
  { t:'', k:'do', s:'plan', w:'St Mark’s Square ticket — Doge’s Palace + Correr', d:'★ BUY ONLINE 30+ DAYS AHEAD (by ~Sep 3) for €30 instead of €35. 2 adults at €30 + 4 reduced at €15 = €120. Beats every Venice city pass by €145.' },
]},
{ d:'2026-10-08', wd:'Thu', city:'VENICE / LIDO', leg:6, note:'Rest day. Lido beaches are free and quiet in October.', items:[]},
{ d:'2026-10-09', wd:'Fri', city:'VENICE / LIDO', leg:6, note:'ANNIVERSARY.', items:[
  { t:'', k:'milestone', s:'tobook', w:'🥂 Dan & Kei’s anniversary — dinner on the canals', d:'Still to book. Musica a Palazzo is the strong candidate for the evening around it.' },
  { t:'', k:'admin', s:'booked', w:'💳 $406 charges today — Osteria della Pista', d:'Visa ••8341.' },
]},
{ d:'2026-10-10', wd:'Sat', city:'LIDO → DOLOMITES', leg:7, note:'Car leg begins. No train.', items:[
  { t:'~09:00', k:'stay', s:'plan', w:'CHECK OUT — Lido', d:'' },
  { t:'~09:30', k:'travel', s:'plan', w:'Alilaguna boat, Lido → Venice Marco Polo (VCE)', d:'~1 h, ~€15pp. No train involved.' },
  { t:'12:00', k:'travel', s:'booked', w:'★ COLLECT THE CAR — Budget, VCE', d:'Ref 02391839US2. Peugeot 5008 or similar, 7 seats, automatic. ⚠️ BRING BOTH INTERNATIONAL DRIVING PERMITS — legally required, cannot be fixed in Italy. ⚠️ Verify whether the card has already been charged.' },
  { t:'~16:00', k:'stay', s:'booked', w:'CHECK IN — Funtnatsch, Laion', d:'39040 Laion (Lajen) BZ. Conf 5740340654, PIN 7729. ⚠️ €57.60 city tax payable AT THE PROPERTY, likely cash.' },
  { t:'', k:'admin', s:'plan', w:'Ask the host about the Südtirol Guest Pass', d:'Free with participating stays incl. holiday apartments. Gives all six free regional trains and buses — would make a Bolzano/Ötzi day free. Covers NO lifts.' },
]},
{ d:'2026-10-11', wd:'Sun', city:'DOLOMITES', leg:7, note:'⚠️ LAST DAY for Resciesa, Ciampinoi, Forcella Sassolungo and the Panorama chair.', items:[
  { t:'', k:'do', s:'plan', w:'★ Keir’s bike day — Ortisei railway trail', d:'Rent in Ortisei (~20 min), ride the old railway grade to Santa Cristina, ~4 km each way, gelato at the turnaround. NOT a gravity park. ⚠️ PHONE AHEAD — Val Gardena half-shuts between seasons. Val Gardena tourist office +39 0471 777777.' },
]},
{ d:'2026-10-12', wd:'Mon', city:'DOLOMITES', leg:7, note:'GREY TURNS 12. Trostburg and the Klausen museum are both shut Mondays, so a mountain day costs nothing in alternatives.', items:[
  { t:'', k:'milestone', s:'plan', w:'🎂 Grey turns 12', d:'' },
  { t:'', k:'do', s:'plan', w:'★ Seceda — the knife-edge ridge', d:'€370 for six. Val Gardena junior rates stop at 15.99, so FOUR of you pay adult €74; only Grey and Keir get €37. Runs 8:30–17:00 from Oct 12.' },
  { t:'', k:'eat', s:'tobook', w:'Grey’s birthday dinner — Gasthof Tschötscherhof', d:'500-year-old farm inn, St Oswald, ~10 min. Warm kitchen ONLY 12:00–14:00 and 18:00–20:30 — book 18:30 and be off the mountain by six.' },
]},
{ d:'2026-10-13', wd:'Tue', city:'DOLOMITES', leg:7, note:'The ONLY day both castles are open.', items:[
  { t:'', k:'do', s:'plan', w:'★ Alpe di Siusi — FAMILY TICKET €65 for all six', d:'Not €132. On THIS lift the junior bracket is "born 2008 or later", so Rhys AND Jude count as juniors. BRING PASSPORTS — an 18-year-old on a family ticket will be questioned.' },
  { t:'', k:'do', s:'free', w:'Oswald von Wolkenstein Weg — free, and built for a 9-year-old', d:'2 h loop past the Hauenstein and Salegg ruins with 15 play stations, a knight’s table and a knight’s sword. Starts at the Alpe di Siusi cableway car park — FREE outdoor parking.' },
  { t:'', k:'eat', s:'plan', w:'★ Törggelen at a mountain farm', d:'€180 for six. New wine, roast chestnuts, speck. Mid-October is peak season in the Isarco valley. ⚠️ You miss both festivals — Gassltörggelen was Sep 18–20, Feldthurns Chestnut Weeks start Oct 17 — but the farm taverns run Oct–Nov.' },
]},
{ d:'2026-10-14', wd:'Wed', city:'DOLOMITES → MALPENSA', leg:8, note:'A scenic drive, explicitly NOT a sightseeing day.', items:[
  { t:'08:30', k:'travel', s:'plan', w:'Leave Laion — A22 to Riva del Garda', d:'Then the cliff-cut Gardesana Occidentale down Garda’s west shore. ⚠️ Riva–Limone closes for rockfall — check ANAS that morning; fallback A22 → Verona → A4.' },
  { t:'12:30', k:'eat', s:'tobook', w:'Long lunch at Gargnano', d:'La Tortuga / La Baia d’Oro / Alla Fassa — small, reserve ahead.' },
  { t:'14:00–15:00', k:'stay', s:'booked', w:'CHECK IN — Osteria della Pista, Casorate Sempione', d:'The property approved this early check-in window. Via Verbano 1, 9 minutes from MXP, restaurant downstairs. $406, charges Oct 9.' },
]},
{ d:'2026-10-15', wd:'Thu', city:'MALPENSA → HOME', leg:8, note:'Non-refundable transatlantic. No heroics.', items:[
  { t:'12:00', k:'travel', s:'booked', w:'★ DROP THE CAR — MXP Terminal 1', d:'Budget ref 02391839US2. Hard deadline.' },
  { t:'16:20', k:'travel', s:'booked', w:'MXP → KEF · Icelandair FI591', d:'Ref AMBVO4. ⚠️ Only 1h15 to connect at Keflavík — the tightest link on the trip.' },
  { t:'19:50', k:'travel', s:'booked', w:'KEF → BWI · Icelandair FI641', d:'Arrives Baltimore 22:15. Then 32 nights in the US with family.' },
]},
];
