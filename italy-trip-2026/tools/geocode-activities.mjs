#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const inputPath = resolve(process.argv[2] || '/tmp/trip-wiki.json')
const outputPath = resolve(process.argv[3] || 'tools/activity-coordinates.json')
const stopFilter = new Set(String(process.env.TRIP_GEOCODE_STOPS || '').split(',').filter(Boolean).map(Number))
const refresh = process.env.TRIP_GEOCODE_REFRESH === '1'
const provider = process.env.TRIP_GEOCODER || 'nominatim'
const nominatimInterval = Number(process.env.NOMINATIM_INTERVAL_MS || 1500)
const pause = milliseconds => new Promise(resolveDelay => setTimeout(resolveDelay, milliseconds))
let lastNominatimRequest = 0
const areaCache = new Map()
let stopCenters = new Map()

// High-value Milan venues whose researched English titles do not resolve
// reliably in open geocoders. These coordinates have been checked directly.
const manualCoordinates = {
  '1-bar-luce-at-fondazione-prada': { latitude: 45.4443737, longitude: 9.2053306, precision: 'manual', label: 'Bar Luce' },
  '1-duomo-rooftop-terraces': { latitude: 45.4641669, longitude: 9.1916121, precision: 'manual', label: 'Duomo di Milano' },
  '1-leonardo-science-museum-the-toti-submarine': { latitude: 45.4617812, longitude: 9.1705869, precision: 'manual', label: 'Museo Nazionale Scienza e Tecnologia Leonardo da Vinci' },
  '1-panzerotti-at-luini': { latitude: 45.465785, longitude: 9.1915481, precision: 'manual', label: 'Luini' },
  '2-la-mandria-park-forest-gravel-spin': { latitude: 45.1663934, longitude: 7.5693639, precision: 'manual', label: 'Parco La Mandria' },
  '2-magic-turin-black-and-white-squares-walk': { latitude: 45.0677551, longitude: 7.6824892, precision: 'area', label: 'Torino' },
  '2-sacra-di-san-michele': { latitude: 45.0979911, longitude: 7.3430477, precision: 'manual', label: 'Sacra di San Michele' },
  '3-l-altro-eden': { latitude: 44.3292361, longitude: 9.2150879, precision: 'manual', label: "L'Altro Eden" },
  '4-gelato-museum-carpigiani': { latitude: 44.5466843, longitude: 11.1933259, precision: 'area', label: "Anzola dell'Emilia" },
  '4-elba-rio-marina-mining-park-minerals': { latitude: 42.8269025, longitude: 10.4091249, precision: 'area', label: 'Rio Marina area' },
  '4-la-finestrella-di-via-piella': { latitude: 44.4987626, longitude: 11.3452134, precision: 'area', label: 'Via Piella area' },
  '4-il-ciocco-bike-park-barga-family-trails-pump-track': { latitude: 44.0739178, longitude: 10.484263, precision: 'area', label: 'Il Ciocco and Barga area' },
  '6-borges-labyrinth-san-giorgio-maggiore': { latitude: 45.4292835, longitude: 12.342414, precision: 'area', label: 'Fondazione Giorgio Cini' },
  '6-cannaregio-and-the-jewish-ghetto': { latitude: 45.4453, longitude: 12.3267, precision: 'area', label: 'Cannaregio and Ghetto area' },
  '6-climb-the-campanile-clock-tower': { latitude: 45.4340361, longitude: 12.3390443, precision: 'manual', label: 'Campanile di San Marco' },
  '6-grand-canal-by-vaporetto-line-1': { latitude: 45.437773, longitude: 12.3355904, precision: 'area', label: 'Grand Canal' },
  '6-homo-faber-if-dates-align': { latitude: 45.4292835, longitude: 12.342414, precision: 'area', label: 'Fondazione Giorgio Cini' },
  '6-peggy-guggenheim-accademia': { latitude: 45.43083, longitude: 12.33154, precision: 'area', label: 'Accademia area' },
  '6-rialto-market-cicchetti-crawl': { latitude: 45.4392, longitude: 12.3346, precision: 'area', label: 'Rialto area' },
  '6-san-pelagio-minotaur-mirror-mazes': { latitude: 45.31425, longitude: 11.82192, precision: 'manual', label: 'Castello di San Pelagio' },
  '6-san-michele-the-cemetery-island': { latitude: 45.446794, longitude: 12.347131, precision: 'manual', label: 'San Michele' },
  '6-st-mark-s-basilica-golden-mosaics': { latitude: 45.4344, longitude: 12.3398, precision: 'manual', label: "St Mark's Basilica" },
  '6-museo-del-precinema-magic-lanterns': { latitude: 45.4002, longitude: 11.87592, precision: 'manual', label: 'Museo del Precinema' },
  '6-villa-foscari-la-malcontenta': { latitude: 45.435278, longitude: 12.201111, precision: 'manual', label: 'Villa Foscari' },
  '6-villa-pisani-labyrinth-stra': { latitude: 45.408889, longitude: 12.011944, precision: 'manual', label: 'Villa Pisani' },
  '7-cinque-torri-open-air-war-museum': { latitude: 46.51, longitude: 12.05194, precision: 'manual', label: 'Cinque Torri' },
  '7-lago-di-carezza': { latitude: 46.410865, longitude: 11.575992, precision: 'manual', label: 'Lago di Carezza' },
  '7-the-drowned-village-of-reschensee': { latitude: 46.81072, longitude: 10.53661, precision: 'manual', label: 'Reschensee drowned tower' },
  'bikepark-alpe-di-mera': { latitude: 45.74567, longitude: 8.08797, precision: 'manual', label: 'Alpe di Mera' },
  'bikepark-cimone-bike-park': { latitude: 44.23, longitude: 10.78, precision: 'manual', label: 'Cimone Bike Park' },
  'bikepark-kronplatz-bike-park': { latitude: 46.7731822, longitude: 11.9424864, precision: 'manual', label: 'Kronplatz Bike Park' },
  'manual-1788458409077': { latitude: 45.4656942, longitude: 9.191145, precision: 'manual', label: 'Spontini Duomo' },
  'manual-1788458409404': { latitude: 45.46555, longitude: 9.19139, precision: 'manual', label: 'Cioccolatitaliani Duomo' },
}

const normalize = value => String(value || '')
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, ' ')
  .trim()

const genericWords = new Set([
  'activity', 'adventure', 'and', 'area', 'at', 'bike', 'castle', 'center', 'centre', 'church',
  'city', 'classic', 'day', 'experience', 'family', 'food', 'from', 'garden', 'house', 'italy',
  'museum', 'park', 'railway', 'the', 'tour', 'trail', 'walk', 'with',
])

function titleWords(activity) {
  const placeWords = new Set(normalize(`${activity.location} ${activity.region || ''}`).split(' '))
  return normalize(activity.title).split(' ').filter(word => (
    word.length >= 4 && !genericWords.has(word) && !placeWords.has(word)
  ))
}

function featurePrecision(feature, activity) {
  const properties = feature.properties || {}
  const featureType = normalize(properties.type || properties.osm_value)
  const areaTypes = new Set(['city', 'town', 'village', 'hamlet', 'locality', 'district', 'county', 'state', 'street', 'road'])
  if (areaTypes.has(featureType)) return 'area'
  const candidate = normalize([
    properties.name, properties.street, properties.locality, properties.district,
    properties.city, properties.county,
  ].filter(Boolean).join(' '))
  const matchingWords = titleWords(activity).filter(word => candidate.includes(word))
  const activityText = normalize(activity.title)
  const osmText = normalize(`${properties.osm_key || ''} ${properties.osm_value || ''} ${properties.type || ''}`)
  if (featureType === 'bank') return 'area'
  if (['bike', 'bikepark'].includes(activity.category)
    && ['memorial', 'monument', 'bank'].some(kind => osmText.includes(kind))) return 'area'
  if (matchingWords.length) return 'venue'
  const compatibleKinds = [
    ['museum', ['museum']], ['museo', ['museum']], ['gallery', ['gallery', 'museum']],
    ['church', ['church', 'place of worship']], ['duomo', ['cathedral', 'church', 'place of worship']],
    ['castle', ['castle', 'fort']], ['palace', ['palace', 'castle']], ['park', ['park', 'garden']],
    ['cafe', ['cafe']], ['restaurant', ['restaurant']], ['tower', ['tower']],
  ]
  return compatibleKinds.some(([word, kinds]) => activityText.includes(word) && kinds.some(kind => osmText.includes(kind)))
    ? 'venue'
    : 'area'
}

async function photon(query, center = null) {
  const url = new URL('https://photon.komoot.io/api/')
  url.searchParams.set('q', query)
  url.searchParams.set('limit', '3')
  url.searchParams.set('lang', 'en')
  if (center) {
    url.searchParams.set('lat', center.latitude)
    url.searchParams.set('lon', center.longitude)
  }
  for (let attempt = 0; attempt < 3; attempt += 1) {
    let response
    try {
      response = await fetch(url, { headers: { 'User-Agent': 'barrett-italy-trip-map/1.0' } })
    } catch (error) {
      if (attempt === 2) throw error
      await pause(1500 * (attempt + 1))
      continue
    }
    if (response.ok) return (await response.json()).features || []
    if (![429, 502, 503, 504].includes(response.status)) throw new Error(`Photon ${response.status}: ${query}`)
    await pause(1000 * (attempt + 1))
  }
  return []
}

async function nominatim(query, center = null) {
  const url = new URL('https://nominatim.openstreetmap.org/search')
  url.searchParams.set('q', query)
  url.searchParams.set('format', 'jsonv2')
  url.searchParams.set('limit', '3')
  url.searchParams.set('countrycodes', 'it')
  url.searchParams.set('addressdetails', '1')
  if (center) {
    url.searchParams.set('viewbox', `${center.longitude - 0.5},${center.latitude + 0.5},${center.longitude + 0.5},${center.latitude - 0.5}`)
  }
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const wait = nominatimInterval - (Date.now() - lastNominatimRequest)
    if (wait > 0) await pause(wait)
    try {
      lastNominatimRequest = Date.now()
      const response = await fetch(url, {
        headers: { 'User-Agent': 'barrett-italy-trip-map/1.0 (private family itinerary)' },
      })
      if (!response.ok) {
        if (![429, 502, 503, 504].includes(response.status) || attempt === 2) {
          throw new Error(`Nominatim ${response.status}: ${query}`)
        }
        await pause(2000 * (attempt + 1))
        continue
      }
      return (await response.json()).map(result => ({
        geometry: { coordinates: [Number(result.lon), Number(result.lat)] },
        properties: {
          name: result.name || result.display_name?.split(',')[0],
          type: result.addresstype || result.type,
          osm_key: result.class,
          osm_value: result.type,
          street: result.address?.road,
          locality: result.address?.suburb,
          district: result.address?.city_district,
          city: result.address?.city || result.address?.town || result.address?.village,
          county: result.address?.county,
          state: result.address?.state,
        },
      }))
    } catch (error) {
      if (attempt === 2) throw error
      await pause(2000 * (attempt + 1))
    }
  }
  return []
}

const search = (query, center = null) => provider === 'nominatim'
  ? nominatim(query, center)
  : photon(query, center)

function chooseAreaFeature(features, activity) {
  const locationNames = activity.location.split(/[\/,]/).map(normalize).filter(Boolean)
  const regionAliases = {
    'aosta valley': ['aosta valley', 'valle daosta'],
    'emilia romagna': ['emilia romagna'],
    friuli: ['friuli', 'friuli venezia giulia'],
    lazio: ['lazio'], liguria: ['liguria'], lombardy: ['lombardy', 'lombardia'],
    'lombardy trentino': ['lombardy', 'lombardia', 'trentino'],
    piedmont: ['piedmont', 'piemonte'], tuscany: ['tuscany', 'toscana'],
    'south tyrol': ['south tyrol', 'sudtirol', 'trentino alto adige'],
    trentino: ['trentino', 'trentino alto adige', 'sudtirol'],
    'trentino alto adige': ['trentino alto adige', 'sudtirol', 'south tyrol'],
    veneto: ['veneto'],
  }
  const expectedRegions = regionAliases[normalize(activity.region)] || [normalize(activity.region)]
  const placeRank = new Map([
    ['city', 8], ['town', 8], ['village', 8], ['hamlet', 7], ['suburb', 6],
    ['locality', 6], ['lake', 5], ['peak', 5], ['station', 5], ['administrative', 0],
  ])
  return features
    .filter(candidate => {
      const [longitude, latitude] = candidate.geometry?.coordinates || []
      return latitude >= 35 && latitude <= 48 && longitude >= 6 && longitude <= 19
    })
    .map((candidate, index) => {
      const name = normalize(candidate.properties?.name)
      const nameScore = locationNames.some(location => name === location) ? 12
        : locationNames.some(location => name && (location.includes(name) || name.includes(location))) ? 6
          : 0
      const candidateRegion = normalize(candidate.properties?.state)
      const regionScore = !candidateRegion || !activity.region ? 0
        : expectedRegions.some(region => candidateRegion.includes(region) || region.includes(candidateRegion)) ? 10
          : -20
      return { candidate, score: nameScore + regionScore + (placeRank.get(normalize(candidate.properties?.type)) ?? 3) - index * 0.01 }
    })
    .sort((left, right) => right.score - left.score)[0]?.candidate
}

function distanceKm(left, right) {
  const radians = degrees => degrees * Math.PI / 180
  const deltaLatitude = radians(right.latitude - left.latitude)
  const deltaLongitude = radians(right.longitude - left.longitude)
  const a = Math.sin(deltaLatitude / 2) ** 2
    + Math.cos(radians(left.latitude)) * Math.cos(radians(right.latitude)) * Math.sin(deltaLongitude / 2) ** 2
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

async function locate(activity) {
  const place = [activity.location, activity.region, 'Italy'].filter(Boolean).join(', ')
  const placeKey = normalize(place)
  let area = areaCache.get(placeKey)
  if (area === undefined) {
    const fallback = chooseAreaFeature(await search(place), activity)
    const stop = stopCenters.get(Number(activity.stop_ordinal))
    area = fallback ? {
      latitude: fallback.geometry.coordinates[1], longitude: fallback.geometry.coordinates[0], precision: 'area',
      label: fallback.properties?.name || fallback.properties?.city || activity.location,
    } : stop?.latitude != null && stop?.longitude != null ? {
      latitude: Number(stop.latitude), longitude: Number(stop.longitude), precision: 'area',
      label: `${stop.name} area`,
    } : null
    areaCache.set(placeKey, area)
  }
  if (!area) return null
  const shortTitle = activity.title.split(/\s+[—–]\s+/)[0].replace(/\([^)]*\)/g, '').trim()
  const queries = [...new Set([
    `${activity.title}, ${place}`,
    `${shortTitle}, ${place}`,
  ])]
  for (const query of queries) {
    const features = await search(query, area)
    const feature = features.find(candidate => {
      const [longitude, latitude] = candidate.geometry?.coordinates || []
      return latitude >= 35 && latitude <= 48 && longitude >= 6 && longitude <= 19
        && featurePrecision(candidate, activity) === 'venue'
        && distanceKm(area, { latitude, longitude }) <= 30
    })
    if (feature) {
      const [longitude, latitude] = feature.geometry.coordinates
      return {
        latitude, longitude,
        precision: featurePrecision(feature, activity),
        label: feature.properties?.name || feature.properties?.city || activity.location,
      }
    }
    await pause(200)
  }
  return area
}

const wiki = JSON.parse(await readFile(inputPath, 'utf8'))
stopCenters = new Map(wiki.stops.map(stop => [Number(stop.ordinal), stop]))
let existing = {}
try { existing = JSON.parse(await readFile(outputPath, 'utf8')) } catch { /* first run */ }

const activities = wiki.activities.filter(activity => !stopFilter.size || stopFilter.has(activity.stop_ordinal))
let completed = 0
for (const activity of activities) {
  if (refresh || !existing[activity.source_key]) {
    try {
      const result = await locate(activity)
      if (result) existing[activity.source_key] = result
    } catch (error) {
      process.stderr.write(`\n${activity.id} ${activity.title}: ${error.message}\n`)
    }
    await pause(250)
  }
  completed += 1
  if (completed % 10 === 0 || completed === activities.length) {
    process.stdout.write(`\rGeocoded ${completed}/${activities.length}`)
    await writeFile(outputPath, `${JSON.stringify(existing, null, 2)}\n`)
  }
}
Object.assign(existing, manualCoordinates)
await writeFile(outputPath, `${JSON.stringify(existing, null, 2)}\n`)
process.stdout.write(`\nSaved ${Object.keys(existing).length} coordinates to ${outputPath}\n`)
