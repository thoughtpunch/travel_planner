import { MapContainer, TileLayer, Marker, Polyline, Popup, Tooltip, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import { STOPS, SIDE, LEGS } from './data.js'

const byKey = Object.fromEntries(STOPS.map((s) => [s.key, s]))

// Numbered, on-brand pin built as a divIcon (no image assets → no bundler icon issues).
function numberedIcon(stop) {
  return L.divIcon({
    className: 'trip-pin-wrap',
    html: `<div class="trip-pin" style="background:${stop.color}">${stop.n}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -16],
  })
}

function legLatLngs(leg) {
  return [
    [byKey[leg.from].lat, byKey[leg.from].lng],
    [byKey[leg.to].lat, byKey[leg.to].lng],
  ]
}

export default function TripMap() {
  return (
    <MapContainer
      center={[42.4, 13.4]}
      zoom={6}
      scrollWheelZoom={false}
      className="trip-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &middot; &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />

      {/* Route segments — sea legs (ferries) dashed blue, rail legs solid terra */}
      {LEGS.map((leg, i) => (
        <Polyline
          key={i}
          positions={legLatLngs(leg)}
          pathOptions={
            leg.mode === 'sea'
              ? { color: '#1B6B8A', weight: 3, dashArray: '2 9', opacity: 0.85 }
              : { color: '#C4531A', weight: 3, opacity: 0.85 }
          }
        >
          <Tooltip sticky>{leg.mode === 'sea' ? '⛴ ' : '🚆 '}{leg.label}</Tooltip>
        </Polyline>
      ))}

      {/* Florence side-dot (part of the Bologna hub) */}
      {SIDE.map((s) => (
        <CircleMarker
          key={s.key}
          center={[s.lat, s.lng]}
          radius={6}
          pathOptions={{ color: '#fff', weight: 2, fillColor: s.color, fillOpacity: 1 }}
        >
          <Tooltip>{s.name} — {s.sub}</Tooltip>
        </CircleMarker>
      ))}

      {/* Numbered city stops */}
      {STOPS.map((stop) => (
        <Marker key={stop.key} position={[stop.lat, stop.lng]} icon={numberedIcon(stop)}>
          <Popup>
            <div className="pop">
              <div className="pop-num" style={{ color: stop.color }}>Stop {stop.n}</div>
              <div className="pop-name">{stop.name}</div>
              <div className="pop-sub">{stop.sub}</div>
              <div className="pop-dates">{stop.dates} · {stop.nights} nights</div>
              <p className="pop-note">{stop.note}</p>
              <a className="pop-link" href={stop.page}>Top 10 &amp; things to do →</a>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
