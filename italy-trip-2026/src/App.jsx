import TripMap from './TripMap.jsx'
import { STOPS, LEGS, TOTAL_NIGHTS } from './data.js'

const legByFrom = Object.fromEntries(LEGS.map((l) => [l.from, l]))

export default function App() {
  return (
    <>
      {/* MASTHEAD */}
      <header className="masthead">
        <div className="masthead-inner">
          <div className="draft-badge">Locked · flights booked</div>
          <div className="trip-label">Barrett Family Italy · Sep 11 – Oct 15, 2026</div>
          <h1 className="trip-title">Italy <em>—</em> Milan back to Milan,<br />by rail</h1>
          <p className="trip-tagline">
            A rail-first family loop: land in Milan, ease down through the lakes and the
            Ligurian coast to the two long work bases — Florence and Rome — then swing back up
            through Bologna, Venice and the Dolomites and out of Malpensa. {TOTAL_NIGHTS} nights,
            no car except the Dolomites, food and family over checklist tourism.
          </p>
          <nav className="topnav">
            <a href="/plan.html">The full plan</a>
            <a href="/trains">Trains &amp; costs</a>
            <a href="/housing">Stays</a>
            <a href="/celebrations">Celebrations</a>
          </nav>
        </div>
      </header>

      {/* MAP */}
      <section className="map-section">
        <div className="wrap">
          <div className="section-label">— The Route</div>
          <h2 className="section-title">The loop, <em>on a real map</em></h2>
          <p className="section-intro">
            Cities placed at their true coordinates. Every leg is a <span className="k-rail">— train</span>
            {' '}(or ferry + funicular); the only wheels of our own are the Dolomites rental car.
            Click a pin for dates and notes.
          </p>
        </div>
        <div className="map-holder">
          <TripMap />
        </div>
        <div className="wrap">
          <p className="map-caption">9 stops · {TOTAL_NIGHTS} nights · all rail · Milan → Rome → Milan</p>
        </div>
      </section>

      {/* ITINERARY */}
      <section className="itin-section">
        <div className="wrap">
          <div className="section-label">— Leg by leg</div>
          <h2 className="section-title">The <em>itinerary</em></h2>
          <ol className="itin">
            {STOPS.map((s) => {
              const leg = legByFrom[s.key]
              return (
                <li key={s.key} className="itin-row">
                  <div className="itin-num" style={{ background: s.color }}>{s.n}</div>
                  <div className="itin-body">
                    <div className="itin-head">
                      <a className="itin-name" href={s.page}>{s.name}</a>
                      <span className="itin-sub">{s.sub}</span>
                      <span className="itin-when">{s.dates} · {s.nights} nts</span>
                    </div>
                    <p className="itin-note">{s.note} <a className="itin-more" href={s.page}>Top 10 &amp; things to do →</a></p>
                    {leg && (
                      <div className="itin-leg">
                        🚆 {leg.label}
                        <span className="itin-arrow"> ↓</span>
                      </div>
                    )}
                  </div>
                </li>
              )
            })}
          </ol>

          <div className="callout">
            <span className="callout-title">Three dates that anchor everything</span>
            <strong>Rhys turns 18 on Sep 18</strong> — the first day in Florence, with a splurge pasta
            dinner. <strong>The anniversary lands Oct 9</strong>, arrival day in the Dolomites, and
            <strong> Grey turns 12 on Oct 12</strong> up in Val Gardena. See the
            {' '}<a className="itin-more" href="/celebrations">celebration plans →</a>
          </div>
        </div>
      </section>

      <footer className="foot">
        <div className="wrap">
          <p>Locked plan · Italy 2026 — flights booked, Milan back to Milan.</p>
          <p className="foot-links">
            <a href="/plan.html">Full plan</a> · <a href="/trains">Trains</a> ·
            <a href="/housing"> Stays</a> · <a href="/celebrations"> Celebrations</a> ·
            <a href="/budget"> Budget</a>
          </p>
        </div>
      </footer>
    </>
  )
}
