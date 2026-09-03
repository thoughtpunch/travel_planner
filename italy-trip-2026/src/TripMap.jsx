import { MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip } from 'react-leaflet'
import L from 'leaflet'

function numberedIcon(stop) {
  return L.divIcon({
    className: 'trip-pin-wrap',
    html: `<div class="trip-pin" style="background:${stop.accent}">${stop.ordinal}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -16],
  })
}

export default function TripMap({ stops, legs }) {
  const bySlug = Object.fromEntries(stops.map(stop => [stop.slug, stop]))
  const routeLegs = legs.filter(leg => bySlug[leg.from_stop] && bySlug[leg.to_stop])

  return <div className="map-holder"><MapContainer
    center={[43.4, 11.3]}
    zoom={6}
    scrollWheelZoom={false}
    className="trip-map"
  >
    <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &middot; &copy; <a href="https://carto.com/attributions">CARTO</a>'
      url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
    />
    {routeLegs.map(leg => <Polyline
      key={leg.id}
      positions={[
        [bySlug[leg.from_stop].latitude, bySlug[leg.from_stop].longitude],
        [bySlug[leg.to_stop].latitude, bySlug[leg.to_stop].longitude],
      ]}
      pathOptions={{ color: leg.mode === 'boat' ? '#1B6B8A' : '#C4531A', weight: 3, opacity: .85, dashArray: leg.mode === 'boat' ? '2 9' : undefined }}
    ><Tooltip sticky>{leg.service || `${leg.origin} to ${leg.destination}`}</Tooltip></Polyline>)}
    {stops.filter(stop => stop.latitude != null && stop.longitude != null).map(stop => <Marker
      key={stop.id}
      position={[stop.latitude, stop.longitude]}
      icon={numberedIcon(stop)}
    ><Popup><div className="pop">
      <div className="pop-num" style={{ color: stop.accent }}>Stop {stop.ordinal}</div>
      <div className="pop-name">{stop.name}</div>
      <div className="pop-sub">{stop.subtitle}</div>
      <div className="pop-dates">{stop.nights} nights</div>
      <p className="pop-note">{stop.summary}</p>
      <a className="pop-link" href={`/activities?where=${encodeURIComponent(stop.slug.replace(/-/g, '_'))}`}>See activities</a>
    </div></Popup></Marker>)}
  </MapContainer></div>
}
