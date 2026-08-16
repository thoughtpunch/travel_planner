/* ============================================================================
 * adventures-data.js — the per-city "stuff the kids will actually love" list
 * ----------------------------------------------------------------------------
 * Rendered by adventures.js into a card grid on each city page, keyed by the
 * page pathname (milan, turin, cinqueterre, florence, rome, venice, dolomites).
 * Full 150-place master list lives in /adventures.csv; this is the route-
 * relevant subset (In base / Day trip / On the way) surfaced on-site.
 *
 * Item shape:
 *   n  name
 *   c  category slug (drives the emoji/color) — see CATS in adventures.js
 *   w  who it's for: array of rhys|jude|grey|keir|all
 *   s  star = unusually high boy-adventure potential
 *   r  reach: 'base' | 'day' | 'way'   (In base / Day trip / On the way here)
 *   b  one-line blurb
 *   l  booking/info link (optional)
 *   img freely-licensed photo URL (optional; Wikimedia Commons). If it fails to
 *       load, adventures.js swaps in an emoji tile — never a broken image.
 * ==========================================================================*/
window.TRIP_ADVENTURES = {

  milan: [
    { n:"Leonardo Science Museum + the Toti submarine", c:"machines", w:["all","keir"], s:true, r:"base", b:"Italy's biggest science museum — Leonardo's machines built full-size, and a whole submarine you walk through.", l:"https://www.museoscienza.org/en", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Nave_sottomarino_-_Museo_scienza_tecnologia_Milano_09676.jpg?width=800" },
    { n:"Museo di Storia Naturale — mineral & gem hall", c:"rock", w:["jude"], r:"base", b:"Meteorites, crystals and cut stones in one of Europe's oldest natural-history museums.", l:"https://www.comune.milano.it", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Veduta_del_Museo_civico_di_storia_naturale_di_Milano.jpg?width=800" },
    { n:"Museum of Senses", c:"weird", w:["all"], r:"base", b:"Hands-on illusions and sensory tricks — pure play." },
    { n:"Duomo → La Scala kids' treasure hunt", c:"hunt", w:["grey","keir"], r:"base", b:"A scavenger hunt through the centre with clues and a prize." },
    { n:"Cremona — violin-making workshop", c:"craft", w:["jude"], r:"day", b:"Watch a luthier build a violin by hand in the world capital of violins." },
    { n:"Bernina Railway from Tirano", c:"transport", w:["jude","all"], s:true, r:"day", b:"Spiral tunnels, viaducts and glaciers on a UNESCO mountain railway into Switzerland." },
    { n:"Rocca di Angera — Lake Maggiore", c:"castle", w:["keir"], r:"day", b:"A huge fortress above the lake, reached by train and boat." },
    { n:"Orrido di Nesso — Lake Como", c:"water", w:["all"], r:"day", b:"A gorge and waterfalls carved through the rock beneath the village." },
  ],

  turin: [
    { n:"Novara — climb inside the San Gaudenzio dome", c:"detour", w:["all"], s:true, r:"way", b:"On the way from Milan: climb inside a 121m dome on masonry walkways. Escher-grade. Open Sundays, age 6+.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Novara_Basilica_di_San_Gaudenzio_Esterno_Cupola_1.jpg?width=800" },
    { n:"Mole Antonelliana — glass lift + Cinema Museum", c:"whoa", w:["keir","all"], s:true, r:"base", b:"A glass elevator shoots up the hollow tower; the museum below is optical illusions and movie sets.", l:"https://www.museocinema.it/en", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Mole_Antonelliana_Torino.JPG?width=800" },
    { n:"Museo Egizio", c:"whoa", w:["keir"], r:"base", b:"The oldest Egyptian museum in the world — mummies and sarcophagi. Under-18 free.", l:"https://museoegizio.it/en/", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Statua_Sekhmet_Museo_Egizio_Torino_Maggio_2025.jpg?width=800" },
    { n:"Torino Sotterranea — underground Turin", c:"underground", w:["all"], s:true, r:"base", b:"Guided walk through siege tunnels, cellars and WWII air-raid shelters.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Pietro_Micca_death_place.jpg?width=800" },
    { n:"Museo Lombroso — criminal anthropology", c:"weird", w:["rhys"], r:"base", b:"A genuinely macabre collection — teen-plus." },
    { n:"Museum of Illusions", c:"weird", w:["all"], r:"base", b:"Rooms of hands-on optical illusions." },
    { n:"Museo Regionale di Scienze Naturali", c:"rock", w:["jude"], r:"base", b:"Geology and mineralogy halls." },
    { n:"Superga rack railway", c:"transport", w:["keir"], r:"base", b:"A historic rack tram grinds up to the hilltop basilica." },
    { n:"Chocolate-making experience", c:"food", w:["grey"], r:"base", b:"Turin is Italy's chocolate capital — make your own." },
    { n:"Damanhur — Temples of Humankind", c:"underground", w:["all"], s:true, r:"day", b:"A hand-dug underground esoteric cathedral of sacred geometry. Best as a Mon day-trip: train to Ivrea + taxi; pre-book the English tour.", l:"https://damanhur.travel/tour/classicvisit-visit-english/" },
    { n:"Sacra di San Michele", c:"castle", w:["all"], r:"day", b:"A dramatic mountaintop abbey (the Name of the Rose one). Train to Sant'Ambrogio + shuttle." },
    { n:"Grotta di Bossea", c:"caves", w:["jude"], r:"day", b:"An Alpine karst show-cave for the rockhound." },
    { n:"Truffle hunt with dogs — Langhe", c:"food", w:["all"], r:"day", b:"Hunt truffles with trained dogs — and September/October is white-truffle season." },
  ],

  cinqueterre: [
    { n:"Genoa — walk through a real submarine", c:"detour", w:["all"], s:true, r:"way", b:"On the way from Turin (you change trains in Genoa anyway): walk bow-to-stern through the S-518 Nazario Sauro at the maritime museum.", l:"https://en.galatamuseodelmare.it/", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Nazario_Sauro_(S_518).jpg?width=800" },
    { n:"Genoa — the Sacro Catino 'Holy Grail'", c:"detour", w:["all"], s:true, r:"way", b:"A green-glass dish the Genoese swore for centuries was the actual Holy Grail, in the cathedral crypt." },
    { n:"Make pesto by hand — Levanto/Genoa", c:"food", w:["grey"], r:"base", b:"Grind real Ligurian pesto with a marble mortar and wooden pestle." },
    { n:"Portovenere & the Byron Grotto", c:"water", w:["all"], s:true, r:"base", b:"A dramatic sea cave and painted harbour at the edge of the gulf — reached by boat.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Portovenere_harbour_and_Doria_Castle,_Liguria,_Italy,_April_2026.jpg?width=800" },
    { n:"Cinque Terre sea-kayak — caves & cliffs", c:"thrill", w:["rhys"], r:"base", b:"Kayak the cliffs and sea caves between the villages. Teen adventure." },
    { n:"Monterosso beach + the coastal ferry", c:"water", w:["keir"], r:"base", b:"The one real Cinque Terre beach — swim, then hop a boat past the cliffs.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Monterosso_al_Mare-panorama-Fegina1.jpg?width=800" },
    { n:"Genova Righi Adventure Park", c:"thrill", w:["rhys"], r:"day", b:"A ropes course strung among Genoa's old hilltop fortifications." },
    { n:"Genova Aquarium", c:"water", w:["keir"], r:"day", b:"Italy's biggest aquarium — sharks, dolphins, a rainforest biosphere." },
    { n:"Antro del Corchia — Apuan Alps cave", c:"caves", w:["jude"], s:true, r:"day", b:"A huge karst cave system inside the marble mountains. Rockhound heaven." },
    { n:"Grotte di Equi", c:"caves", w:["jude"], r:"day", b:"Caves right in the Apuan Alps." },
  ],

  florence: [
    { n:"Carrara — 4×4 marble quarry tour", c:"detour", w:["jude"], s:true, r:"way", b:"On the Chiavari→Florence day: ride a Land Rover into the working white-marble quarries. The operator can hold your bags.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Carrara_marble_quarry_face.jpg?width=800" },
    { n:"Pietrasanta — the marble-carving town", c:"craft", w:["jude"], r:"way", b:"Sculptors' studios, bronze foundries, the free Museo dei Bozzetti — raw stone in the morning, finished art in the afternoon.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Piazza_Duomo_(Pietrasanta).jpg?width=800" },
    { n:"Pisa — leaning tower + the death fresco", c:"detour", w:["all"], r:"way", b:"You change trains at Pisa anyway: climb the tower (age 8+) and see the macabre Triumph of Death fresco." },
    { n:"Scuola del Cuoio — the leather school", c:"craft", w:["jude"], s:true, r:"base", b:"Jude's leatherworking: a working leather school inside Santa Croce runs hands-on craft sessions.", l:"https://www.scuoladelcuoio.com/en/", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Scuola_del_cuoio_Firenze.jpg?width=800" },
    { n:"La Specola — minerals + anatomical waxes", c:"rock", w:["jude"], s:true, r:"base", b:"The reopened Medici mineral hall plus the famous anatomical wax models. A 10-minute walk from your door.", l:"https://www.sma.unifi.it/vp-245-la-specola.html", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Universit%C3%A0_di_Firenze_Museo_Zoologico_%22La_Specola%22_(89368).jpg?width=800" },
    { n:"Le Arti Orafe — set your own gemstone", c:"craft", w:["jude"], r:"base", b:"Set a real gemstone onto a silver ring and take it home.", l:"https://artiorafe.it/en/craft-experience/" },
    { n:"Museo Galileo", c:"machines", w:["all"], r:"base", b:"Old scientific instruments, globes and telescopes — on-brand weird-science." },
    { n:"Palazzo Vecchio — secret passages", c:"secret", w:["all"], s:true, r:"base", b:"A guide unlocks hidden doors, stairs and roof spaces inside the old palace.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Palazzo_vecchio_Florence.jpg?width=800" },
    { n:"Brunelleschi's dome climb", c:"whoa", w:["all"], r:"base", b:"Climb up between the double shells of the great Duomo dome.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Cupola_di_santa_maria_del_fiore_dal_campanile_di_giotto,_01.JPG?width=800" },
    { n:"Florentine paper-marbling workshop", c:"craft", w:["grey"], r:"base", b:"Swirl and make your own marbled paper by hand." },
    { n:"Fresh pasta + gelato class", c:"food", w:["grey"], r:"base", b:"Roll Tuscan pasta, then churn gelato to finish.", l:"https://www.florencetown.com/" },
    { n:"Uffizi family treasure hunt", c:"hunt", w:["grey"], r:"base", b:"A kid-focused hunt that turns the Uffizi into a game." },
    { n:"Scarperia — knife & blade making", c:"craft", w:["jude"], r:"day", b:"A historic blade town with hands-on cutlery workshops. One of Jude's 'workshops'." },
    { n:"Volterra — carve alabaster", c:"craft", w:["jude"], r:"day", b:"Carve alabaster stone in the ancient Etruscan workshop town." },
    { n:"Labirinto della Masone — bamboo maze", c:"maze", w:["all"], s:true, r:"day", b:"The largest bamboo labyrinth in the world, near Parma.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Il_Labirinto_della_Masone_visto_dallalto,_Labirinto_della_Masone,_Fontanellato_(PR),_Italia,_2019_foto_G.Ferretti.jpg?width=800" },
    { n:"Bologna — hands-on pasta class", c:"food", w:["grey"], r:"day", b:"Make tagliatelle and tortellini by hand in Italy's food capital." },
    { n:"Modena — traditional balsamic acetaia", c:"food", w:["grey"], r:"day", b:"See real balsamic age in barrels, then taste the syrupy DOP stuff." },
    { n:"Motor Valley — Ferrari · Lamborghini · Ducati", c:"machines", w:["jude"], s:true, r:"day", b:"Supercar museums and live factory lines, all within an hour of Bologna." },
  ],

  rome: [
    { n:"Orvieto — the double-helix well + caves", c:"detour", w:["all"], s:true, r:"way", b:"On the Florence→Rome day: the Pozzo di San Patrizio is two spiral staircases that never meet, right at the funicular top — plus Etruscan cave-tunnels.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Pozzo_di_San_Patrizio,_Orvieto.jpg?width=800" },
    { n:"Colosseum Underground", c:"secret", w:["all"], s:true, r:"base", b:"Down into the hypogeum — the tunnels and lifts beneath the arena floor.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Hypogeum_1_(15005526662).jpg?width=800" },
    { n:"Basilica di San Clemente — 3 layers down", c:"underground", w:["all"], r:"base", b:"Descend through a church, an older church, and a pagan temple with a running stream." },
    { n:"The Catacombs", c:"underground", w:["all"], r:"base", b:"Kilometres of early-Christian burial tunnels under the city." },
    { n:"Capuchin Crypt — the bone chapel", c:"weird", w:["all"], s:true, r:"base", b:"Rooms decorated entirely with the bones of 3,700 monks.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Capuchin_Crypt_-_DPLA_-_103cc5af0b9e4d62334af9db890b7c8b.jpg?width=800" },
    { n:"Museum of the Holy Souls in Purgatory", c:"weird", w:["rhys"], r:"base", b:"A tiny, genuinely bizarre museum of scorch-marks 'left by souls'." },
    { n:"Palazzo Spada — the forced-perspective trick", c:"maze", w:["all"], r:"base", b:"Borromini's optical-illusion colonnade that looks four times its real length." },
    { n:"Quartiere Coppedè", c:"architecture", w:["all"], r:"base", b:"A fairy-tale quarter of monsters, spiders and dreamlike facades — free to wander.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Palace_in_quartiere_copped%C3%A8.jpg?width=800" },
    { n:"Castel Sant'Angelo", c:"castle", w:["all"], r:"base", b:"Fortress ramps and corridors, and the pope's secret escape passage.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/RomaCastelSantAngelo.jpg?width=800" },
    { n:"Centrale Montemartini", c:"machines", w:["jude"], r:"base", b:"Ancient Roman statues posed among the giant machines of a 1912 power station." },
    { n:"Gladiator school — Scuola Gladiatori", c:"thrill", w:["keir"], s:true, r:"base", b:"Tunic on, wooden sword, real moves, a mini-tournament and a certificate. Age 6+.", l:"https://www.gruppostoricoromano.it/?lang=en" },
    { n:"Pizza + gelato class for kids", c:"food", w:["grey"], r:"base", b:"Roll dough, top a pizza in a real oven, then churn gelato.", l:"https://www.inromecooking.com/tour/kids-and-family-classes/pizza-making-and-gelato-class-for-kids/" },
    { n:"Roman Forum family treasure hunt", c:"hunt", w:["grey"], r:"base", b:"A story-driven hunt that brings the ruins alive for kids." },
    { n:"Bomarzo — the Park of the Monsters", c:"architecture", w:["all"], s:true, r:"day", b:"Giant grotesque stone monsters scattered through a Renaissance garden — an outdoor fantasy level.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Monster_in_Parco_dei_Mostri_(Bomarzo).jpg?width=800" },
    { n:"Civita di Bagnoregio — the 'dying city'", c:"architecture", w:["all"], r:"day", b:"A cliff-top town reached only by a long footbridge." },
    { n:"Falconer for a Day — La Selvotta", c:"animals", w:["keir"], s:true, r:"day", b:"A bird of prey flies free and lands back on your glove. Under 20km from Rome." },
    { n:"Pitigliano + the Vie Cave", c:"rock", w:["jude"], r:"day", b:"A town carved from volcanic tufa, ringed by Etruscan roads cut as deep trenches through the rock." },
  ],

  venice: [
    { n:"Murano — watch glassblowing, make a bead", c:"craft", w:["keir"], s:true, r:"base", b:"A maestro turns molten glass into a horse in two minutes; then you make your own bead.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Murano_furnace_and_pipe.jpg?width=800" },
    { n:"Doge's Palace — Secret Itineraries", c:"secret", w:["all"], s:true, r:"base", b:"Behind locked doors: the offices, interrogation rooms and prison passages of the old republic.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Doge%27s_Palace_Venice_sea_facade.jpg?width=800" },
    { n:"The Doge's Palace armoury", c:"whoa", w:["keir"], r:"base", b:"Suits of armour, swords and crossbows — the sword-and-armour fix. Under-18 free." },
    { n:"The Venetian Arsenal", c:"whoa", w:["all"], r:"base", b:"The enormous medieval shipyard that once built a galley a day.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Arsenale_di_Venezia_gate.jpg?width=800" },
    { n:"Borges Labyrinth — San Giorgio Maggiore", c:"maze", w:["all"], r:"base", b:"A hedge maze based on the Borges story, on its own island." },
    { n:"Scala Contarini del Bovolo", c:"architecture", w:["all"], r:"base", b:"An external spiral tower-staircase that looks almost impossible." },
    { n:"Learn to row Venetian-style", c:"water", w:["rhys"], r:"base", b:"A standing-up rowing lesson in a traditional boat." },
    { n:"Kayak the lagoon & hidden canals", c:"thrill", w:["rhys"], r:"base", b:"Paddle the quiet back-canals and out into the lagoon." },
    { n:"Carnival mask-making workshop", c:"craft", w:["grey"], r:"base", b:"Make and paint your own Venetian mask." },
    { n:"Venetian cicchetti cooking class", c:"food", w:["grey"], r:"base", b:"Make the city's own bar snacks in a local's home.", l:"https://cesarine.com/en" },
    { n:"Hidden-city treasure hunt", c:"hunt", w:["all"], r:"base", b:"Secret symbols, alleys and clues across Venice." },
    { n:"Lido beach + vaporetto rides", c:"water", w:["keir"], r:"base", b:"A real beach island to run on — and the water-buses are half the fun. (MuMu's island.)" },
    { n:"Villa Pisani labyrinth — Stra", c:"maze", w:["all"], s:true, r:"day", b:"A famous historic hedge maze with a tower at the centre.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Labirinto_villa_Pisani_1.JPG?width=800" },
    { n:"San Pelagio — Minotaur & mirror mazes", c:"maze", w:["all"], r:"day", b:"Two very different mazes at a castle near Padua." },
    { n:"Museo del Precinema — magic lanterns", c:"weird", w:["all"], r:"day", b:"Magic lanterns and proto-cinema devices in Padua." },
    { n:"Grotte di Oliero — by boat", c:"caves", w:["jude"], r:"day", b:"Cave springs you enter by boat. Rockhound + water." },
    { n:"Museo Nicolis — cars & machines", c:"machines", w:["jude"], r:"day", b:"Cars, motorcycles and machines near Verona." },
  ],

  dolomites: [
    { n:"Seceda — the knife-edge ridge", c:"mountain", w:["all"], s:true, r:"base", b:"A cable car to the tilted Odle ridgeline at 2,500m. Open into November — golden larches in October.", l:"https://www.seceda.it/en/summer", img:"https://commons.wikimedia.org/wiki/Special:FilePath/The_Dolomites_from_Seceda.jpg?width=800" },
    { n:"Alpe di Siusi — Europe's biggest meadow", c:"mountain", w:["all"], s:true, r:"base", b:"Gentle meadow walks to huts with playgrounds and animals under the Sciliar. Birthday-day base.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Gr%C3%B6dner_Dolomiten_Seiser-Alm_Hi_res.jpg?width=800" },
    { n:"Hike & Cheese Workshop", c:"food", w:["grey"], s:true, r:"base", b:"Make fresh cheese by hand with a farmer (in English) — Grey's Oct 12 birthday centrepiece. Confirm the date; season ends mid-Oct." },
    { n:"Gostner Schwaige — alpine dairy hut", c:"food", w:["all"], r:"base", b:"A working hut making its own cheese, butter and ricotta — a special mountain lunch." },
    { n:"Sassolungo — the 'coffin lift'", c:"thrill", w:["rhys"], s:true, r:"base", b:"Tiny open two-person cabins float you to a high saddle. Closes Oct 11 — ride it your first day.", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Langkofel_group_from_the_Sella_pass_2016.jpg?width=800" },
    { n:"Col Raiser + Puez-Odle walks", c:"mountain", w:["all"], r:"base", b:"A quieter gondola into the nature park, under the Odle spires." },
    { n:"Bletterbach — the fossil canyon", c:"rock", w:["jude"], s:true, r:"day", b:"Walk into an 8km gorge slicing through 40 million years of rock — ammonites, reptile tracks. Jude's best day.", l:"https://www.bletterbach.info/en/", img:"https://commons.wikimedia.org/wiki/Special:FilePath/Bletterbach_HDR.jpg?width=800" },
    { n:"Val di Fassa / Predazzo — geology trails", c:"rock", w:["jude"], r:"day", b:"Volcanic and sedimentary Dolomite geology with a mineral museum, close to Val Gardena." },
    { n:"Lagazuoi — WWI tunnels in the mountain", c:"thrill", w:["rhys"], s:true, r:"day", b:"Hike through war tunnels cut straight into the Dolomite rock." },
    { n:"Via ferrata — Averau / Gran Cir", c:"thrill", w:["rhys"], r:"day", b:"An approachable first via ferrata for the teens, with a guide (weather permitting)." },
    { n:"Törggelen — the autumn farm dinner", c:"food", w:["all"], r:"day", b:"October-only: roast chestnuts, new wine and strudel at a farm tavern in the Eisacktal." },
    { n:"Roter Hahn farm — bread & strudel baking", c:"food", w:["grey"], r:"day", b:"A hands-on farm baking session, arranged directly — apple-harvest season." },
    { n:"Museum Gherdëina — Ortisei", c:"rock", w:["jude"], r:"base", b:"Local Dolomite fossils and minerals — a good rainy-day fix." },
  ],

};
