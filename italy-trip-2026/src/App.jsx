import TripMap from './TripMap.jsx'
import { STOPS, LEGS, TOTAL_NIGHTS } from './data.js'

const legByFrom = Object.fromEntries(LEGS.map((l) => [l.from, l]))

export default function App() {
  return (
    <>
      {/* MASTHEAD */}
      <header className="masthead">
        <div className="masthead-inner">
          <div className="draft-badge">Draft v2 · The Big Loop</div>
          <div className="trip-label">Family Expedition · Sept 6 – Nov 20, 2026</div>
          <h1 className="trip-title">Italy <em>—</em> One Big Loop,<br />Trains &amp; Ferries</h1>
          <p className="trip-tagline">
            Rome to Rome, counter-clockwise: down to Naples and Sicily, up the spine to the
            Bologna hub and the Dolomites, two weeks with family on the Lido, then across the
            Adriatic to Croatia and home. {TOTAL_NIGHTS} nights, no backtracking, no mid-trip flights.
          </p>
          <nav className="topnav">
            <a href="/activities">Activities by kid</a>
            <a href="/adventures">Boy adventures</a>
            <a href="/worldschooling">Worldschool families</a>
            <a href="/plan.html">Detailed base notes (v1)</a>
          </nav>
        </div>
      </header>

      {/* MAP */}
      <section className="map-section">
        <div className="wrap">
          <div className="section-label">— The Route</div>
          <h2 className="section-title">The loop, <em>on a real map</em></h2>
          <p className="section-intro">
            Cities placed at their true coordinates. <span className="k-rail">— rail</span> legs are solid;
            <span className="k-sea"> ·· ferry</span> legs (Naples→Sicily, Venice→Croatia, Croatia→Rome) are dashed.
            Click a pin for dates and notes.
          </p>
        </div>
        <div className="map-holder">
          <TripMap />
        </div>
        <div className="wrap">
          <p className="map-caption">8 stops · {TOTAL_NIGHTS} nights · 2 ferries · start + end Rome</p>
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
                      <span className="itin-name">{s.name}</span>
                      <span className="itin-sub">{s.sub}</span>
                      <span className="itin-when">{s.dates} · {s.nights} nts</span>
                    </div>
                    <p className="itin-note">{s.note}</p>
                    {leg && (
                      <div className="itin-leg">
                        {leg.mode === 'sea' ? '⛴' : '🚆'} {leg.label}
                        <span className="itin-arrow"> ↓</span>
                      </div>
                    )}
                  </div>
                </li>
              )
            })}
          </ol>

          <div className="callout">
            <span className="callout-title">Two things to confirm</span>
            <strong>Rhys's 18th (Sept 18)</strong> falls in Naples, not Rome — an 18th in the pizza
            capital, or stretch the Rome opener. And the only long transit days are
            <strong> Sicily→Bologna</strong> and <strong>Croatia→Rome</strong> — unavoidable with
            Sicily south and Croatia northeast, but one travel day each.
          </div>
        </div>
      </section>

      <footer className="foot">
        <div className="wrap">
          <p>Draft v2 · the big loop · Italy 2026 — replaces the earlier four-base plan.</p>
          <p className="foot-links">
            <a href="/activities">Activities</a> · <a href="/adventures">Adventures</a> ·
            <a href="/worldschooling"> Worldschool</a> · <a href="/plan.html"> Detailed base notes (v1)</a>
          </p>
        </div>
      </footer>
    </>
  )
}
