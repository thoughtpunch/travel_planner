import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Popup, ScaleControl, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'

const CHOSEN_STATUSES = new Set(['shortlisted', 'selected', 'booked', 'done'])

const STATUS_LABELS = {
  option: 'Unplanned',
  shortlisted: 'Shortlisted',
  selected: 'Selected',
  booked: 'Booked',
  done: 'Done',
  cancelled: 'Cancelled',
  skipped: 'Won\u2019t do',
}

const isCoordinate = (value, minimum, maximum) => {
  const number = Number(value)
  return Number.isFinite(number) && number >= minimum && number <= maximum
}

const activityPoint = activity => {
  if (!isCoordinate(activity.latitude, -90, 90) || !isCoordinate(activity.longitude, -180, 180)) return null
  return [Number(activity.latitude), Number(activity.longitude)]
}

const precisionValue = activity => activity.coordinate_precision
  || activity.geocode_precision
  || activity.precision
  || ''

const isAreaPrecision = activity => ['area', 'approximate'].includes(String(precisionValue(activity)).toLowerCase())

const precisionNote = (activity, visuallySpread = false) => {
  const precision = String(precisionValue(activity)).toLowerCase()
  if (precision === 'venue' || precision === 'exact') return 'Pin is at the venue.'
  if (precision === 'manual') return 'Pin was manually placed.'
  if (visuallySpread) return 'Approximate area pin — visually spread from its shared area center.'
  if (precision === 'area' || precision === 'approximate') return 'Approximate pin — area-level location.'
  return 'Pin location is approximate.'
}

const stableActivityKey = (activity, index) => String(
  activity.id || activity.source_key || activity.title || index,
)

// Geocoders can return the same city/area center for many broad searches. Keep
// that real coordinate for links and exact pins, but fan approximate pins into
// a small, deterministic spiral so every result remains clickable.
function spreadColocatedAreaPins(entries) {
  const groups = new Map()
  entries.forEach((entry, index) => {
    const coordinateKey = entry.point.join(',')
    if (!groups.has(coordinateKey)) groups.set(coordinateKey, [])
    groups.get(coordinateKey).push({ ...entry, sourceIndex: index })
  })

  const spreadByIndex = new Map()
  groups.forEach(group => {
    if (group.length < 2) return
    const approximate = group
      .filter(entry => isAreaPrecision(entry.activity))
      .sort((left, right) => stableActivityKey(left.activity, left.sourceIndex)
        .localeCompare(stableActivityKey(right.activity, right.sourceIndex)) || left.sourceIndex - right.sourceIndex)

    approximate.forEach((entry, spiralIndex) => {
      const angle = spiralIndex * Math.PI * (3 - Math.sqrt(5))
      const radiusMetres = 40 * Math.sqrt(spiralIndex + 1)
      const latitudeRadians = entry.point[0] * Math.PI / 180
      const latitudeOffset = (radiusMetres * Math.sin(angle)) / 111320
      const longitudeScale = Math.max(Math.cos(latitudeRadians), 0.2)
      const longitudeOffset = (radiusMetres * Math.cos(angle)) / (111320 * longitudeScale)
      spreadByIndex.set(entry.sourceIndex, {
        displayPoint: [entry.point[0] + latitudeOffset, entry.point[1] + longitudeOffset],
        visuallySpread: true,
      })
    })
  })

  return entries.map((entry, index) => ({
    ...entry,
    displayPoint: spreadByIndex.get(index)?.displayPoint || entry.point,
    visuallySpread: spreadByIndex.has(index),
  }))
}

function FitVisiblePins({ points }) {
  const map = useMap()
  const pointsKey = points.map(point => point.join(',')).join('|')

  useEffect(() => {
    if (!points.length) return
    map.invalidateSize({ pan: false })
    map.fitBounds(L.latLngBounds(points), {
      animate: false,
      maxZoom: 15,
      padding: [34, 34],
    })
  }, [map, pointsKey]) // eslint-disable-line react-hooks/exhaustive-deps

  return null
}

/**
 * Map of the activities currently visible in the explorer.
 *
 * `activities` should be the already-filtered collection. `onPlan` receives
 * the clicked activity, so the parent can open its existing planning flow.
 */
export default function ActivityMap({ activities = [], stops = [], onPlan }) {
  const stopNames = useMemo(() => new Map(stops.map(stop => [Number(stop.ordinal), stop.name])), [stops])
  const mappedActivities = useMemo(() => spreadColocatedAreaPins(activities
    .map(activity => ({ activity, point: activityPoint(activity) }))
    .filter(entry => entry.point)), [activities])
  const missingCount = activities.length - mappedActivities.length

  if (!mappedActivities.length) {
    return <section className="activity-map activity-map-empty" aria-label="Activity map">
      <strong>No mapped activities in these results.</strong>
      <span>{activities.length ? `${activities.length} ${activities.length === 1 ? 'activity needs' : 'activities need'} coordinates.` : 'Change or clear the filters to see activity pins.'}</span>
    </section>
  }

  const points = mappedActivities.map(entry => entry.displayPoint)

  return <section className="activity-map" aria-label="Map of filtered activities">
    <header className="activity-map-head">
      <div>
        <strong>{mappedActivities.length} mapped</strong>
        {missingCount > 0 && <span> · {missingCount} without coordinates</span>}
      </div>
      <div className="activity-map-legend" aria-label="Map pin legend">
        <span><i className="activity-map-key chosen" />Picked</span>
        <span><i className="activity-map-key option" />Not picked</span>
      </div>
    </header>
    <div className="activity-map-canvas">
      <MapContainer
        center={points[0]}
        zoom={12}
        scrollWheelZoom={false}
        className="activity-map-leaflet"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &middot; &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <ScaleControl imperial={false} />
        <FitVisiblePins points={points} />
        {mappedActivities.map(({ activity, point, displayPoint, visuallySpread }, index) => {
          const chosen = CHOSEN_STATUSES.has(activity.selection_status)
          const status = STATUS_LABELS[activity.selection_status] || activity.selection_status || 'Unplanned'
          const locationName = activity.location || stopNames.get(Number(activity.stop_ordinal)) || 'Location not listed'
          const mapsUrl = activity.map_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(point.join(','))}`
          return <CircleMarker
            key={activity.id || activity.source_key || `${point.join('-')}-${index}`}
            center={displayPoint}
            radius={8}
            pathOptions={{
              color: '#fffaf2',
              weight: 2,
              fillColor: chosen ? '#28745a' : '#d6402b',
              fillOpacity: 1,
            }}
          >
            <Popup>
              <div className="activity-map-popup">
                <span className={`activity-map-status ${chosen ? 'chosen' : 'option'}`}>{status}</span>
                <strong>{activity.title || 'Untitled activity'}</strong>
                <span>{locationName}</span>
                <small>{precisionNote(activity, visuallySpread)}</small>
                <div className="activity-map-popup-actions">
                  <a href={mapsUrl} target="_blank" rel="noreferrer">Google Maps</a>
                  {typeof onPlan === 'function' && <button type="button" onClick={() => onPlan(activity)}>{chosen ? 'Plan' : 'Choose & plan'}</button>}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        })}
      </MapContainer>
    </div>
  </section>
}
