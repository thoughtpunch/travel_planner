import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api.js'
import ActivityMap from './ActivityMap.jsx'
import TripMap from './TripMap.jsx'

const VIEWS = [
  ['overview', 'At a glance'],
  ['itinerary', 'Itinerary'],
  ['activities', 'Activities'],
  ['costs', 'Costs'],
]

const viewPath = key => key === 'overview' ? '/' : `/${key}`
const viewFromLocation = () => {
  const slug = location.pathname.replace(/^\/+|\/+$/g, '')
  if (VIEWS.some(([key]) => key === slug)) return slug
  const legacyHash = location.hash.slice(1)
  return VIEWS.some(([key]) => key === legacyHash) ? legacyHash : 'overview'
}

const STATUS_LABELS = {
  option: 'Option', shortlisted: 'Shortlist', selected: 'Selected', booked: 'Booked',
  done: 'Done', cancelled: 'Cancelled', skipped: 'Won\u2019t do', tobook: 'To book', plan: 'Plan', free: 'Free',
  estimate: 'Estimate', unknown: 'Unknown', pending: 'Pending', paid: 'Paid', partial: 'Part paid',
  partial_refund: 'Part refunded', refunded: 'Refunded',
}

const AUDIENCE_LABELS = {
  all: 'Everyone', parents: 'Dan & Kei', kids: 'Kids', rhys: 'Rhys',
  jude: 'Jude', grey: 'Grey', keir: 'Keir',
}

const CATEGORY_LABELS = {
  machines: 'Machines', rock: 'Rocks & gems', weird: 'Weird museum', hunt: 'Treasure hunt',
  craft: 'Craft & workshop', transport: 'Transport', castle: 'Castle & fort', water: 'Water & boats',
  detour: 'On-the-way stop', whoa: 'Big whoa', underground: 'Underground', secret: 'Behind the scenes',
  maze: 'Maze & illusion', thrill: 'Climb & thrill', food: 'Food you make', architecture: 'Architecture',
  animals: 'Animals', caves: 'Caves', mountain: 'Mountains', art: 'Art & masters', sight: 'Landmark & view',
  dining: 'Dining out', nature: 'Nature & gardens', church: 'Church & relics', market: 'Market & food hall',
  bike: 'Trail biking', bikepark: 'Bike park',
}

const REACH_LABELS = { base: 'In town', way: 'On the way', day: 'Day trip', far: 'Own trip' }

const CATEGORY_ICONS = {
  machines: '⚙️', rock: '🪨', weird: '💀', hunt: '🗺️', craft: '🛠️', transport: '🚡',
  castle: '🏰', water: '🚣', detour: '🚂', whoa: '😮', underground: '🕳️', secret: '🔑',
  maze: '🌀', thrill: '🧗', food: '🍕', architecture: '🏛️', animals: '🦅', caves: '🦇',
  mountain: '⛰️', art: '🖼️', sight: '📸', dining: '🍽️', nature: '🌿', church: '⛪',
  market: '🛍️', bike: '🚵', bikepark: '🚵',
}

const PEOPLE_FILTERS = [
  ['rhys', 'Rhys'], ['jude', 'Jude'], ['grey', 'Grey'], ['keir', 'Keir'],
  ['parents', 'Dan & Kei'], ['all', 'All'],
]
const PRICE_BANDS = [
  ['free', 'Free / donation', cost => cost?.midpoint === 0],
  ['u50', '$0–50', cost => cost && cost.midpoint > 0 && cost.midpoint * 1.16 < 50],
  ['50', '$50–100', cost => cost && cost.midpoint * 1.16 >= 50 && cost.midpoint * 1.16 < 100],
  ['100', '$100–200', cost => cost && cost.midpoint * 1.16 >= 100 && cost.midpoint * 1.16 < 200],
  ['200', '$200–300', cost => cost && cost.midpoint * 1.16 >= 200 && cost.midpoint * 1.16 < 300],
  ['300', '$300+', cost => cost && cost.midpoint * 1.16 >= 300],
  ['unk', 'Unpriced', cost => !cost],
]
const REALISTIC_LIMIT_EUR = 172
const EASY_YES_EUR = 86

const audienceKeys = value => String(value || 'all').toLowerCase().split(/\s*[·,]\s*/).filter(Boolean)

// Original explorer fallback for rows without a hand-researched override. It
// only accepts patterns that can be converted to a whole-family number without
// guessing; everything else stays explicitly unpriced.
const parseListedPartyCost = item => {
  const text = String(item.estimated_cost_text || '').trim()
  if (!text) return null
  const number = value => Number(String(value).replace(/,/g, ''))
  const adults = item.stop_ordinal <= 2 ? 2 : 3
  let match = text.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:[-–]\s*(\d[\d.,]*)\s*)?(?:for six|for 6|\/\s*6\b)/i)
  if (match) return { low: number(match[1]), high: number(match[2] || match[1]), note: 'quoted for 6', confidence: '' }
  match = text.match(/\(~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)(?:\s*[-–]\s*(\d[\d.,]*))?\s*for six\)/i)
  if (match) return { low: number(match[1]), high: number(match[2] || match[1]), note: 'quoted for 6', confidence: '' }
  if (/free/i.test(text) && !/(?:€|EUR|\$|USD)\s*\d/.test(text)) return { low: 0, high: 0, note: 'free', confidence: '' }
  if (/under[- ]?18[^·]*free|under[- ]?18 EU free/i.test(text)) {
    match = text.match(/adults?\s*~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)/i) || text.match(/~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*pp/i)
    if (match) return { low: number(match[1]) * adults, high: number(match[1]) * adults, note: `${adults} paying (under-18s free)`, confidence: '' }
  }
  match = text.match(/under[- ]?(\d{1,2})s?\s*(?:free|FREE)/i)
  if (match) {
    const cutoff = Number(match[1])
    const ages = [40, 40, item.stop_ordinal <= 2 ? 17 : 18, 16, 12, 9]
    const payers = ages.filter(age => age >= cutoff).length
    const adultPrice = text.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:adult|pp)/i) || text.match(/adults?\s*~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)/i)
    if (adultPrice) return { low: number(adultPrice[1]) * payers, high: number(adultPrice[1]) * payers, note: `${payers} paying (under-${cutoff} free)`, confidence: '' }
  }
  match = text.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:[-–]\s*(?:€|EUR|\$|USD)?\s*(\d[\d.,]*)\s*)?pp/i)
  if (match) return { low: number(match[1]) * 6, high: number(match[2] || match[1]) * 6, note: '6 × per-person', confidence: '' }
  return null
}

const partyCost = item => {
  const researched = item.source_details?.party_cost
  if (researched) return {
    low: Number(researched.low), high: Number(researched.high), midpoint: Number(researched.midpoint),
    note: researched.note || '', confidence: researched.confidence || '',
  }
  const parsed = parseListedPartyCost(item)
  if (parsed) return { ...parsed, midpoint: Math.round((parsed.low + parsed.high) / 2) }
  if (item.estimated_cost != null) return {
    low: Number(item.estimated_cost), high: Number(item.estimated_cost), midpoint: Number(item.estimated_cost),
    note: '', confidence: '',
  }
  return null
}

const statusBucket = item => {
  if (['shortlisted', 'selected'].includes(item.selection_status)) return 'want'
  if (['booked', 'done'].includes(item.selection_status)) return 'booked'
  if (item.selection_status === 'skipped') return 'skip'
  if (item.selection_status === 'cancelled') return 'cancelled'
  return 'none'
}

const fmtDate = (value, options = {}) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-US', {
    timeZone: 'UTC', month: 'short', day: 'numeric', ...options,
  }).format(new Date(`${value}T12:00:00Z`))
}

const fmtMoney = (value, currency = 'USD') => value == null ? '—' : new Intl.NumberFormat('en-US', {
  style: 'currency', currency, maximumFractionDigits: value % 1 ? 2 : 0,
}).format(value)

const toUSD = (value, currency) => value == null ? 0 : value * (currency === 'EUR' ? 1.16 : 1)
const budgetImpact = cost => cost.booking_status === 'cancelled'
  ? toUSD(cost.net_paid_amount || 0, cost.currency)
  : toUSD(cost.amount || 0, cost.currency)

const hasExactTime = value => /^\d{2}:\d{2}$/.test(value || '')
const isFlexibleTime = value => !value || /^all[ -]?day$/i.test(value.trim())
const itineraryTime = value => isFlexibleTime(value) ? 'All day / time TBD' : value

const ACTIVITY_FILTER_PARAMS = {
  where: 'where', price: 'budget', who: 'who', reach: 'reach', type: 'type', status: 'status',
}
const ACTIVITY_SORT_OPTIONS = [
  ['leg', 'Trip order'], ['title', 'Title'], ['city', 'City'], ['region', 'Region'],
  ['cost-low', 'Party cost: low first'], ['cost-high', 'Party cost: high first'],
]

const urlToken = value => String(value || '')
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .replace(/[’']/g, '')
  .replace(/&/g, ' and ')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .replace(/^_+|_+$/g, '')

const filterUrlValue = (options, value) => {
  const option = options.find(([optionValue]) => optionValue === value)
  return urlToken(option?.[1] || value)
}

const filterValueFromUrl = (options, rawValue) => {
  const token = urlToken(rawValue)
  return options.find(([value, label]) => (
    rawValue === value || token === urlToken(value) || token === urlToken(label)
  ))?.[0]
}

const activityFilterOptions = data => {
  const usedCategories = [...new Set(data.activities.map(item => item.category).filter(Boolean))]
  return {
    where: data.stops
      .filter(stop => data.activities.some(item => item.stop_ordinal === stop.ordinal))
      .map(stop => [String(stop.ordinal), stop.name]),
    price: PRICE_BANDS.map(([key, label]) => [key, label]),
    who: PEOPLE_FILTERS,
    reach: Object.entries(REACH_LABELS),
    type: usedCategories.map(key => [key, `${CATEGORY_ICONS[key] || '✨'} ${CATEGORY_LABELS[key] || key}`]),
    status: [['want', 'Want'], ['booked', 'Booked'], ['cancelled', 'Cancelled'], ['skip', 'Won’t do (hidden)'], ['none', 'Unplanned']],
  }
}

function activityStateFromUrl(options, fallbackStop = 0) {
  const params = new URLSearchParams(location.search)
  const values = (name, group) => [...new Set(params.getAll(name)
    .flatMap(value => value.split(','))
    .map(value => filterValueFromUrl(options[group], value))
    .filter(Boolean))]
  const where = values('where', 'where')
  const legacyStop = params.get('stop')
  if (!where.length && legacyStop) {
    const stop = filterValueFromUrl(options.where, legacyStop)
    if (stop) where.push(stop)
  }
  if (!where.length && fallbackStop) where.push(String(fallbackStop))
  const requestedSort = filterValueFromUrl(ACTIVITY_SORT_OPTIONS, params.get('sort')) || 'leg'
  return {
    filters: {
      where,
      price: values('budget', 'price'),
      who: values('who', 'who'),
      reach: values('reach', 'reach'),
      type: values('type', 'type'),
      status: values('status', 'status'),
    },
    query: params.get('q') || '',
    mustDo: params.get('must') === '1',
    realistic: params.get('realistic') !== '0',
    sort: requestedSort,
  }
}

function calendarUrl(activity) {
  if (!activity.scheduled_date) return ''
  const compact = value => value.replace(/[-:]/g, '')
  let dates
  if (hasExactTime(activity.scheduled_time)) {
    const start = new Date(`${activity.scheduled_date}T${activity.scheduled_time}:00Z`)
    const end = new Date(start.getTime() + 2 * 60 * 60 * 1000)
    const stamp = date => date.toISOString().slice(0, 19).replace(/[-:]/g, '')
    dates = `${stamp(start)}/${stamp(end)}`
  } else {
    const end = new Date(`${activity.scheduled_date}T12:00:00Z`)
    end.setUTCDate(end.getUTCDate() + 1)
    dates = `${compact(activity.scheduled_date)}/${compact(end.toISOString().slice(0, 10))}`
  }
  const params = new URLSearchParams({
    action: 'TEMPLATE', text: activity.title, dates,
    details: [activity.notes, activity.user_url, location.origin].filter(Boolean).join('\n\n'),
    location: activity.location || '', ctz: 'Europe/Rome',
  })
  return `https://calendar.google.com/calendar/render?${params}`
}

export default function App() {
  const [data, setData] = useState(null)
  const [view, setView] = useState(viewFromLocation)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    try { setData(await api.load()); setError('') }
    catch (err) { setError(err.message) }
  }

  useEffect(() => { load() }, [])
  useEffect(() => {
    if (location.hash) history.replaceState({}, '', viewPath(viewFromLocation()))
    const onPopState = () => setView(viewFromLocation())
    addEventListener('popstate', onPopState)
    return () => removeEventListener('popstate', onPopState)
  }, [])

  const navigate = (nextView) => {
    history.pushState({}, '', viewPath(nextView))
    setView(nextView)
    scrollTo({ top: 0, behavior: 'instant' })
  }

  const updateActivity = async (id, patch) => {
    setData(current => ({ ...current, activities: current.activities.map(item =>
      item.id === id ? { ...item, ...patch } : item
    ) }))
    try {
      const saved = await api.patchActivity(id, patch)
      setData(current => ({ ...current, activities: current.activities.map(item => item.id === id ? saved : item) }))
      setNotice('Activity saved')
    } catch (err) { setError(err.message); await load() }
  }

  const updateCost = async (id, patch) => {
    setData(current => ({ ...current, costs: current.costs.map(item =>
      item.id === id ? { ...item, ...patch } : item
    ) }))
    try {
      const saved = await api.patchCost(id, patch)
      setData(current => ({ ...current, costs: current.costs.map(item => item.id === id ? saved : item) }))
      setNotice('Cost saved')
      await load()
    } catch (err) { setError(err.message); await load() }
  }

  if (error && !data) return <FatalError error={error} retry={load} />
  if (!data) return <div className="loading"><span />Loading the trip…</div>

  const selectedCount = data.activities.filter(a => ['shortlisted', 'selected', 'booked', 'done'].includes(a.selection_status)).length
  const toBookCount = data.days.flatMap(d => d.items).filter(i => i.status === 'tobook').length

  return <div className="shell">
    <header className="sidebar">
      <a className="brand" href="/" onClick={event => { event.preventDefault(); navigate('overview') }} aria-label="Italy trip overview">
        <small>Barrett family · Sep 11 – Oct 15, 2026</small>
        <strong>Italy <em>—</em> the trip</strong>
      </a>
      <div className="trip-stamp"><span>Booked itinerary</span><strong>34 nights</strong><span>6 travelers · 8 stops</span></div>
      <nav aria-label="Trip wiki">{VIEWS.map(([key, label]) =>
        <a key={key} href={viewPath(key)} onClick={event => { event.preventDefault(); navigate(key) }} className={view === key ? 'active' : ''}>{label}
          {key === 'activities' && <b>{selectedCount}</b>}
          {key === 'itinerary' && toBookCount > 0 && <b className="attention">{toBookCount}</b>}
        </a>)}</nav>
      <div className="stop-index">{data.stops.map(stop =>
        <button key={stop.id} onClick={() => {
          sessionStorage.setItem('activityStop', String(stop.ordinal)); navigate('activities')
        }}><i style={{ background: stop.accent }} /><span>{stop.name}<small>{fmtDate(stop.date_start)}–{fmtDate(stop.date_end)}</small></span></button>)}</div>
      <p className="storage-note">Saved to the shared trip database</p>
    </header>
    <main>
      <MobileHeader view={view} navigate={navigate} />
      {view === 'overview' && <Overview data={data} />}
      {view === 'itinerary' && <Itinerary data={data} />}
      {view === 'activities' && <Activities data={data} updateActivity={updateActivity} reload={load} />}
      {view === 'costs' && <Costs data={data} updateCost={updateCost} setData={setData} reload={load} />}
    </main>
    {(notice || error) && <div className={`toast ${error ? 'error' : ''}`} role="status" onAnimationEnd={() => { setNotice(''); if (data) setError('') }}>{error || notice}</div>}
  </div>
}

function MobileHeader({ view, navigate }) {
  return <header className="mobile-head"><a href="/" onClick={event => { event.preventDefault(); navigate('overview') }}>Italy 2026</a><span>{VIEWS.find(v => v[0] === view)?.[1]}</span></header>
}

function PageHead({ title, intro, actions }) {
  return <header className="page-head"><div><h1>{title}</h1>{intro && <p>{intro}</p>}</div>{actions}</header>
}

function Overview({ data }) {
  const unpaid = data.costs.filter(c => ['pending', 'partial'].includes(c.payment_status))
  const openLegs = data.legs.filter(l => l.booking_status !== 'booked')
  return <div className="page">
    <PageHead title="At a glance" intro="Confirmed trip facts, transport and places to sleep." />
    <section className="facts-band">
      <div><strong>{data.stops.length}</strong><span>stops</span></div>
      <div><strong>{data.legs.filter(l => l.booking_status === 'booked').length}/{data.legs.length}</strong><span>legs booked</span></div>
      <div><strong>{data.activities.filter(a => a.selection_status === 'booked').length}</strong><span>activities booked</span></div>
      <div><strong>{unpaid.length}</strong><span>payments open</span></div>
    </section>
    {(openLegs.length > 0 || unpaid.length > 0) && <section className="attention-strip"><strong>Still open</strong>
      <span>{openLegs.map(l => `${fmtDate(l.date)} ${l.origin} to ${l.destination}`).join(' · ') || 'All transport booked'}</span>
      <span>{unpaid.length} pending or partial payment{unpaid.length === 1 ? '' : 's'}</span></section>}
    <section className="map-section"><h2>The route</h2><p className="section-intro">The booked loop, with every overnight stop in sequence.</p><TripMap stops={data.stops} legs={data.legs} /></section>
    <section><h2>Stops</h2><div className="route-list">{data.stops.map((stop, index) =>
      <div className="route-stop" key={stop.id}>
        <div className="route-mark"><span style={{ borderColor: stop.accent }}>{stop.ordinal}</span>{index < data.stops.length - 1 && <i />}</div>
        <div><h3>{stop.name}</h3><p>{stop.subtitle}</p></div>
        <time>{fmtDate(stop.date_start)}–{fmtDate(stop.date_end)}<small>{stop.nights} nights</small></time>
        <p className="route-summary">{stop.summary}</p>
      </div>)}</div></section>
    <section><h2>Travel legs</h2><div className="table-wrap"><table><thead><tr><th>Date</th><th>Route</th><th>Service</th><th>Time</th><th>Status</th></tr></thead>
      <tbody>{data.legs.map(leg => <tr key={leg.id}>
        <td>{fmtDate(leg.date)}</td><td><strong>{leg.origin}</strong><span className="route-arrow">to</span>{leg.destination}</td>
        <td>{leg.service}<small>{leg.confirmation}</small></td><td>{leg.departure_time}–{leg.arrival_time}</td><td><Status value={leg.booking_status} /></td>
      </tr>)}</tbody></table></div></section>
    <section><h2>Stays</h2><div className="stay-list">{data.stays.map(stay => <article key={stay.id}>
      <div><strong>{stay.name}</strong><span>{stay.address}</span></div>
      <div><span>Check in</span><strong>{fmtDate(stay.checkin_date)} {stay.checkin_time}</strong></div>
      <div><span>Check out</span><strong>{fmtDate(stay.checkout_date)} {stay.checkout_time}</strong></div>
      {stay.confirmation && <code>{stay.confirmation}</code>}
    </article>)}</div></section>
  </div>
}

function Itinerary({ data }) {
  const [filter, setFilter] = useState('all')
  const scheduled = useMemo(() => {
    const byDate = {}
    data.activities.filter(a => a.scheduled_date && ['selected', 'booked', 'done'].includes(a.selection_status))
      .forEach(a => { (byDate[a.scheduled_date] ||= []).push(a) })
    Object.values(byDate).forEach(items => items.sort((a, b) => {
      const aFlexible = isFlexibleTime(a.scheduled_time)
      const bFlexible = isFlexibleTime(b.scheduled_time)
      if (aFlexible !== bFlexible) return aFlexible ? -1 : 1
      return hasExactTime(a.scheduled_time) && hasExactTime(b.scheduled_time)
        ? a.scheduled_time.localeCompare(b.scheduled_time)
        : a.title.localeCompare(b.title)
    }))
    return byDate
  }, [data.activities])
  const days = data.days.map(day => ({ ...day, scheduled: scheduled[day.date] || [] })).filter(day => {
    if (filter === 'all') return true
    if (filter === 'tobook') return day.items.some(i => i.status === 'tobook')
    if (filter === 'activities') return day.scheduled.length > 0
    return day.items.some(i => i.kind === filter)
  })
  return <div className="page itinerary-page">
    <PageHead title="Itinerary" intro="Booked facts plus selected activities that have a date." />
    <div className="filters" role="group" aria-label="Filter itinerary">{[['all','Everything'],['activities','Scheduled activities'],['tobook','Still to book'],['travel','Travel'],['stay','Stays']].map(([key,label]) =>
      <button key={key} className={filter === key ? 'active' : ''} onClick={() => setFilter(key)}>{label}</button>)}</div>
    <div className="timeline">{days.map(day => <article className="day" key={day.id}>
      <div className="date-rail"><time><b>{fmtDate(day.date, { weekday: 'short' }).split(' ')[0]}</b>{fmtDate(day.date)}</time><i /></div>
      <div className="day-body"><header><h2>{day.city}</h2>{day.note && <p>{day.note}</p>}</header>
        {day.scheduled.map(activity => <div className={`event scheduled${isFlexibleTime(activity.scheduled_time) ? ' flexible-time' : ''}`} key={`a-${activity.id}`}><time>{itineraryTime(activity.scheduled_time)}</time><div><strong>{activity.title}</strong><Status value={activity.selection_status} /><p>{activity.location}{activity.actual_cost != null ? ` · ${fmtMoney(activity.actual_cost, activity.currency)}` : ''} · <a href={calendarUrl(activity)} target="_blank" rel="noreferrer">Google Calendar</a></p></div></div>)}
        {day.items.filter(item => filter === 'all' ? true : filter === 'tobook' ? item.status === 'tobook' : filter === 'activities' ? false : item.kind === filter).map(item =>
          <div className={`event${isFlexibleTime(item.time) ? ' flexible-time' : ''}`} key={item.id}><time>{itineraryTime(item.time)}</time><div><strong>{item.title}</strong><Status value={item.status} /><p>{item.detail}</p></div></div>)}
      </div>
    </article>)}</div>
  </div>
}

function Activities({ data, updateActivity, reload }) {
  const remembered = Number(sessionStorage.getItem('activityStop') || 0)
  const filterOptions = useMemo(() => activityFilterOptions(data), [data])
  const initialUrlState = useMemo(() => activityStateFromUrl(filterOptions, remembered), []) // eslint-disable-line react-hooks/exhaustive-deps
  const [filters, setFilters] = useState(initialUrlState.filters)
  const [query, setQuery] = useState(initialUrlState.query)
  const [mustDo, setMustDo] = useState(initialUrlState.mustDo)
  const [realistic, setRealistic] = useState(initialUrlState.realistic)
  const [sort, setSort] = useState(initialUrlState.sort)
  const [filterMenuVersion, setFilterMenuVersion] = useState(0)
  const [adding, setAdding] = useState(false)
  const [planning, setPlanning] = useState(null)
  const [selectedIds, setSelectedIds] = useState(() => new Set())
  const [planningQueue, setPlanningQueue] = useState([])
  const [batchPlanning, setBatchPlanning] = useState(false)
  const [batchTotal, setBatchTotal] = useState(0)
  const [batchBusy, setBatchBusy] = useState(false)
  const [batchError, setBatchError] = useState('')
  const initialStop = Number(initialUrlState.filters.where[0] || remembered || 1)
  const [draft, setDraft] = useState({ title: '', stop_ordinal: initialStop, location: '', estimated_cost: '', scheduled_date: '' })
  useEffect(() => { sessionStorage.removeItem('activityStop') }, [])
  useEffect(() => {
    const params = new URLSearchParams()
    Object.entries(ACTIVITY_FILTER_PARAMS).forEach(([group, param]) => {
      filters[group].forEach(value => params.append(param, filterUrlValue(filterOptions[group], value)))
    })
    if (query) params.set('q', query)
    if (mustDo) params.set('must', '1')
    if (!realistic) params.set('realistic', '0')
    if (sort !== 'leg') params.set('sort', filterUrlValue(ACTIVITY_SORT_OPTIONS, sort))
    const search = params.toString()
    const nextUrl = `${location.pathname}${search ? `?${search}` : ''}`
    if (`${location.pathname}${location.search}` !== nextUrl) {
      history.replaceState(history.state, '', nextUrl)
    }
  }, [filters, query, mustDo, realistic, sort, filterOptions])

  const toggleFilter = (group, value) => setFilters(current => ({
    ...current,
    [group]: current[group].includes(value) ? current[group].filter(item => item !== value) : [...current[group], value],
  }))
  const hiddenCount = data.activities.filter(item => item.selection_status === 'skipped').length
  const activeCount = data.activities.length - hiddenCount
  const showingHidden = filters.status.includes('skip')
  const shown = data.activities.filter(item => {
    const people = audienceKeys(item.audience)
    const searchText = `${item.title} ${item.location} ${item.region} ${item.audience} ${item.description} ${item.logistics} ${item.category}`.toLowerCase()
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean)
    const cost = partyCost(item)
    if (item.selection_status === 'skipped' && !showingHidden) return false
    return (!filters.where.length || filters.where.includes(String(item.stop_ordinal)))
      && (!filters.price.length || filters.price.some(key => PRICE_BANDS.find(band => band[0] === key)?.[2](cost)))
      && (!filters.who.length || people.includes('all') || people.some(person => filters.who.includes(person)))
      && (!filters.reach.length || filters.reach.includes(item.travel_scope))
      && (!filters.type.length || filters.type.includes(item.category))
      && (!filters.status.length || filters.status.includes(statusBucket(item)))
      && (!mustDo || item.is_featured)
      && (!realistic || showingHidden || !cost || cost.midpoint <= REALISTIC_LIMIT_EUR || item.source_details?.is_shortlist)
      && terms.every(term => searchText.includes(term))
  }).sort((a, b) => {
    if (sort === 'cost-low' || sort === 'cost-high') {
      const left = partyCost(a)?.midpoint
      const right = partyCost(b)?.midpoint
      if (left == null && right == null) return 0
      if (left == null) return 1
      if (right == null) return -1
      return sort === 'cost-low' ? left - right : right - left
    }
    if (sort === 'title') return a.title.localeCompare(b.title)
    if (sort === 'city') return a.location.localeCompare(b.location) || a.title.localeCompare(b.title)
    if (sort === 'region') return a.region.localeCompare(b.region) || a.title.localeCompare(b.title)
    return a.stop_ordinal - b.stop_ordinal || a.title.localeCompare(b.title)
  })
  const shownKey = shown.map(item => item.id).join(',')
  useEffect(() => {
    const visible = new Set(shown.map(item => item.id))
    setSelectedIds(current => new Set([...current].filter(id => visible.has(id))))
  }, [shownKey]) // eslint-disable-line react-hooks/exhaustive-deps
  const selectedItems = shown.filter(item => selectedIds.has(item.id))
  const draftStop = data.stops.find(stop => stop.ordinal === Number(draft.stop_ordinal))
  const selected = data.activities.filter(a => ['shortlisted', 'selected', 'booked', 'done'].includes(a.selection_status))
  const curated = data.activities.filter(item => item.selection_status !== 'skipped' && item.source_details?.is_shortlist)
  const selectedTotal = selected.reduce((sum, item) => sum + (item.actual_cost ?? partyCost(item)?.midpoint ?? 0), 0)
  const curatedTotal = curated.reduce((sum, item) => sum + (partyCost(item)?.midpoint ?? 0), 0)
  const hiddenForBudget = realistic ? data.activities.filter(item => {
    const cost = partyCost(item)
    return item.selection_status !== 'skipped' && cost && cost.midpoint > REALISTIC_LIMIT_EUR && !item.source_details?.is_shortlist
  }).length : 0
  const singleStop = filters.where.length === 1 ? data.stops.find(stop => String(stop.ordinal) === filters.where[0]) : null
  const stopActivities = singleStop ? data.activities.filter(item => item.stop_ordinal === singleStop.ordinal && item.selection_status !== 'skipped') : []
  const resetFilters = (showEverything = false) => {
    setFilters({ where: [], price: [], who: [], reach: [], type: [], status: [] })
    setQuery(''); setMustDo(false); setRealistic(!showEverything); setSort('leg')
    setFilterMenuVersion(value => value + 1)
  }
  const showAllHidden = () => {
    setFilters({ where: [], price: [], who: [], reach: [], type: [], status: ['skip'] })
    setQuery(''); setMustDo(false); setRealistic(false); setSort('leg')
    setFilterMenuVersion(value => value + 1)
  }
  const toggleSelected = id => setSelectedIds(current => {
    const next = new Set(current)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    return next
  })
  const changeVisibility = async (ids, action) => {
    setBatchBusy(true); setBatchError('')
    try {
      await api.patchActivitiesBulk(ids, action)
      setSelectedIds(current => new Set([...current].filter(id => !ids.includes(id))))
      await reload()
    } catch (err) { setBatchError(err.message) }
    finally { setBatchBusy(false) }
  }
  const prepareForPlanning = item => item.selection_status === 'skipped'
    ? { ...item, selection_status: 'selected' }
    : item
  const planOne = item => {
    setBatchPlanning(false); setPlanningQueue([]); setBatchTotal(0)
    setPlanning(item)
  }
  const planSelected = () => {
    if (!selectedItems.length) return
    const [first, ...rest] = selectedItems
    setBatchPlanning(true); setBatchTotal(selectedItems.length); setPlanningQueue(rest)
    setPlanning(prepareForPlanning(first))
  }
  const closePlanning = () => {
    setPlanning(null); setPlanningQueue([]); setBatchPlanning(false); setBatchTotal(0)
  }
  const advancePlanning = () => {
    if (!batchPlanning || !planningQueue.length) {
      setSelectedIds(new Set()); closePlanning(); return
    }
    const [next, ...rest] = planningQueue
    setPlanningQueue(rest); setPlanning(prepareForPlanning(next))
  }
  const add = async (event) => {
    event.preventDefault()
    await api.createActivity({ ...draft, stop_ordinal: Number(draft.stop_ordinal), estimated_cost: draft.estimated_cost === '' ? null : Number(draft.estimated_cost), scheduled_date: draft.scheduled_date || null })
    setAdding(false); setDraft({ title: '', stop_ordinal: initialStop, location: '', estimated_cost: '', scheduled_date: '' }); await reload()
  }
  return <div className="page activities-page">
    <PageHead title="Activities" intro={`${activeCount} researched options${hiddenCount ? ` · ${hiddenCount} hidden` : ''}. Choose one, give it a date, and it appears on the itinerary.`} actions={<button className="primary" onClick={() => setAdding(!adding)}>Add activity</button>} />
    {adding && <form className="add-form" onSubmit={add}>
      <label>Activity<input required value={draft.title} onChange={e => setDraft({...draft,title:e.target.value})} /></label>
      <label>Stop<select value={draft.stop_ordinal} onChange={e => setDraft({...draft,stop_ordinal:e.target.value,scheduled_date:''})}>{data.stops.map(s => <option key={s.id} value={s.ordinal}>{s.name}</option>)}</select></label>
      <label>Location<input value={draft.location} onChange={e => setDraft({...draft,location:e.target.value})} /></label>
      <label>Estimate (€)<input type="number" min="0" value={draft.estimated_cost} onChange={e => setDraft({...draft,estimated_cost:e.target.value})} /></label>
      <label>Date<input type="date" min={draftStop?.date_start || '2026-09-11'} max={draftStop?.date_end || '2026-10-15'} value={draft.scheduled_date} onChange={e => setDraft({...draft,scheduled_date:e.target.value})} />{draftStop && <small>{fmtDate(draftStop.date_start)}–{fmtDate(draftStop.date_end)}</small>}</label>
      <button className="primary">Save activity</button>
    </form>}
    <section className="selection-summary"><strong>{selected.length} picked</strong><span>{selected.filter(a => a.scheduled_date).length} on the itinerary</span><span>{selected.filter(a => !a.scheduled_date).length} need a date</span><span>{fmtMoney(selectedTotal, 'EUR')} tracked</span></section>
    <section className="activity-explorer" aria-label="Activity explorer filters">
      <div className="activity-search-row">
        <input type="search" placeholder="Search title, place, description…" value={query} onChange={e => setQuery(e.target.value)} />
        <button type="button" className={mustDo ? 'filter-toggle active' : 'filter-toggle'} onClick={() => setMustDo(value => !value)}>★ Must-do only</button>
        <button type="button" className={realistic ? 'filter-toggle active' : 'filter-toggle'} onClick={() => setRealistic(value => !value)}>💸 Realistic budget</button>
        <button type="button" className="filter-reset" onClick={() => resetFilters()}>Reset</button>
        <strong className="activity-count">{showingHidden ? `${shown.length} shown` : `${shown.length} of ${activeCount}`}</strong>
      </div>
      <div className="activity-budget-note">{hiddenForBudget ? `${hiddenForBudget} over ~$200 hidden` : 'All price levels shown'}</div>
      <div className="activity-filter-row" key={filterMenuVersion}>
        <FilterMenu label="Where" group="where" selected={filters.where} toggle={toggleFilter} options={filterOptions.where} />
        <FilterMenu label="Budget" group="price" selected={filters.price} toggle={toggleFilter} options={filterOptions.price} />
        <FilterMenu label="Who" group="who" selected={filters.who} toggle={toggleFilter} options={filterOptions.who} />
        <FilterMenu label="How far" group="reach" selected={filters.reach} toggle={toggleFilter} options={filterOptions.reach} />
        <FilterMenu label="Type" group="type" selected={filters.type} toggle={toggleFilter} options={filterOptions.type} />
        <FilterMenu label="Status" group="status" selected={filters.status} toggle={toggleFilter} options={filterOptions.status} />
        <label className="activity-sort"><span>Sort</span><select value={sort} onChange={event => setSort(event.target.value)}>{ACTIVITY_SORT_OPTIONS.map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select></label>
      </div>
    </section>
    <ActivityMap activities={shown} stops={data.stops} onPlan={planOne} />
    {selectedItems.length > 0 && <aside className="batch-bar" role="toolbar" aria-label="Selected activity actions">
      <strong>{selectedItems.length} selected</strong>
      <button type="button" className="primary" onClick={planSelected} disabled={batchBusy}>Plan / book selected</button>
      <button type="button" className="batch-hide" onClick={() => changeVisibility(selectedItems.map(item => item.id), selectedItems.every(item => item.selection_status === 'skipped') ? 'restore' : 'hide')} disabled={batchBusy}>{selectedItems.every(item => item.selection_status === 'skipped') ? 'Restore selected' : 'Hide selected'}</button>
      <button type="button" className="batch-clear" onClick={() => setSelectedIds(new Set())} disabled={batchBusy}>Clear</button>
    </aside>}
    {batchError && <p className="modal-error batch-error">{batchError}</p>}
    {singleStop && <section className="leg-cost-summary"><strong>{singleStop.name}</strong><span>{fmtDate(singleStop.date_start)}–{fmtDate(singleStop.date_end)}</span><span><b>{stopActivities.filter(item => partyCost(item)?.midpoint === 0).length}</b> free</span><span><b>{stopActivities.filter(item => { const cost = partyCost(item); return cost && cost.midpoint > 0 && cost.midpoint <= EASY_YES_EUR }).length}</b> under $100</span><span><b>{stopActivities.filter(item => { const cost = partyCost(item); return cost && cost.midpoint > EASY_YES_EUR && cost.midpoint <= REALISTIC_LIMIT_EUR }).length}</b> $100–200</span></section>}
    {curated.length > 0 && <section className="curated-summary"><strong>Shortlist</strong><span>{curated.length} picked · <b>{fmtMoney(curatedTotal, 'EUR')}</b> ≈ {fmtMoney(Math.round(curatedTotal * 1.16), 'USD')}</span><span>{curated.filter(item => (partyCost(item)?.midpoint ?? 0) > REALISTIC_LIMIT_EUR).length} over $200</span></section>}
    <div className="activity-results-head"><span>Plan</span><span>Activity and details</span><span>Party cost</span></div>
    <div className="activity-list">
      {shown.map(item => <ActivityRow key={item.id} item={item} selected={selectedIds.has(item.id)} onToggle={() => toggleSelected(item.id)} onPlan={() => planOne(item)} onVisibility={() => changeVisibility([item.id], item.selection_status === 'skipped' ? 'restore' : 'hide')} busy={batchBusy} />)}
      {shown.length === 0 && <div className="activity-empty"><strong>No activities match those filters.</strong><button type="button" onClick={showingHidden ? showAllHidden : () => resetFilters(true)}>{showingHidden ? 'Show all hidden activities' : 'Show everything'}</button></div>}
    </div>
    {planning && <ActivityModal key={planning.id} item={planning} stop={data.stops.find(stop => stop.ordinal === planning.stop_ordinal)} update={updateActivity} reload={reload} close={closePlanning} onSaved={advancePlanning} queueLabel={batchPlanning ? `${batchTotal - planningQueue.length} of ${batchTotal} selected` : ''} hasNext={batchPlanning && planningQueue.length > 0} />}
  </div>
}

function FilterMenu({ label, group, selected, toggle, options }) {
  const menu = useRef(null)
  useEffect(() => {
    const closeOutside = event => {
      if (menu.current?.open && !menu.current.contains(event.target)) menu.current.open = false
    }
    const closeWithEscape = event => {
      if (event.key === 'Escape' && menu.current?.open) {
        menu.current.open = false
        menu.current.querySelector('summary')?.focus()
      }
    }
    document.addEventListener('pointerdown', closeOutside)
    document.addEventListener('keydown', closeWithEscape)
    return () => {
      document.removeEventListener('pointerdown', closeOutside)
      document.removeEventListener('keydown', closeWithEscape)
    }
  }, [])
  const choose = value => {
    toggle(group, value)
    if (menu.current) menu.current.open = false
  }
  const selectedText = selected
    .map(value => options.find(([optionValue]) => optionValue === value)?.[1])
    .filter(Boolean)
    .join(', ')
  return <details className="filter-menu" ref={menu}>
    <summary className={selected.length ? 'has-selection' : ''} aria-label={`${label}: ${selectedText || 'Any'}`} title={selectedText || label}><span>{selectedText || label}</span></summary>
    <div className="filter-menu-panel">{options.map(([value, text]) => <button type="button" key={value} className={selected.includes(value) ? 'active' : ''} onClick={() => choose(value)}>{text}</button>)}</div>
  </details>
}

function ActivityRow({ item, selected, onToggle, onPlan, onVisibility, busy }) {
  const chosen = ['selected', 'booked', 'done'].includes(item.selection_status)
  const managed = ['shortlisted', 'selected', 'booked', 'done', 'cancelled', 'skipped'].includes(item.selection_status)
  const people = audienceKeys(item.audience)
  const cost = partyCost(item)
  const bikeDetails = item.category === 'bikepark' ? ['Fit', 'Rentals', '2026 close', 'Lifts', 'Kid-friendly', 'Nearest leg']
    .filter(key => item.source_details?.[key]).map(key => [key, item.source_details[key]]) : []
  const distinctNotes = item.notes && item.notes !== item.description
  return <article className={`activity ${item.image_url ? 'has-photo' : 'no-photo'} ${chosen ? 'chosen' : ''} ${item.selection_status === 'cancelled' ? 'cancelled' : ''} ${item.selection_status === 'skipped' ? 'wont-do' : ''}`}>
    {item.image_url && <div className="activity-photo"><img src={item.image_url} alt={item.title} loading="lazy" decoding="async" onError={event => { const card = event.currentTarget.closest('.activity'); event.currentTarget.parentElement.hidden = true; card.classList.remove('has-photo'); card.classList.add('no-photo') }} /></div>}
    <div className="activity-content">
      <header className="activity-title">
        <span className="stop-number">{item.stop_ordinal || '—'}</span>
        <div><div className="activity-kicker"><span>{CATEGORY_ICONS[item.category] || '✨'} {CATEGORY_LABELS[item.category] || item.category}</span>{item.is_featured && <b>★ Must-do</b>}{item.source_details?.is_shortlist && <b className="keep-badge">Keep</b>}</div><h2>{item.title}</h2></div>
      </header>
      {item.description && <p className="activity-description">{item.description}</p>}
      <dl className="activity-facts">
        <div><dt>Where</dt><dd>{item.location}{item.region ? `, ${item.region}` : ''}</dd></div>
        <div><dt>Best for</dt><dd className="audience-list">{people.map(person => <span className={`person person-${person}`} key={person}>{AUDIENCE_LABELS[person] || person}</span>)}</dd></div>
        <div><dt>Reach</dt><dd>{REACH_LABELS[item.travel_scope] || item.travel_scope}</dd></div>
        <div><dt>Total for six</dt><dd className="party-cost">{cost ? <><strong>{cost.midpoint === 0 ? 'Free' : fmtMoney(cost.midpoint, 'EUR')}</strong>{cost.midpoint > 0 && <span>≈ {fmtMoney(Math.round(cost.midpoint * 1.16), 'USD')}</span>}{cost.high !== cost.low && <small>range {fmtMoney(cost.low, 'EUR')}–{fmtMoney(cost.high, 'EUR')}</small>}</> : 'Unpriced'}</dd></div>
      </dl>
      <div className="activity-cost-detail">
        <p><b>As listed</b>{item.estimated_cost_text || '—'}</p>
        {cost?.note && <p><b>Party estimate</b>{cost.note}{cost.confidence && <small>{cost.confidence} confidence</small>}</p>}
        {item.actual_cost != null && <p><b>Actual cost</b>{fmtMoney(item.actual_cost, item.currency)}</p>}
        {item.cost && <p><b>Payment</b>{STATUS_LABELS[item.cost.payment_status] || item.cost.payment_status}{item.cost.paid_amount > 0 && ` · ${fmtMoney(item.cost.paid_amount, item.cost.currency)} paid`}{item.cost.refunded_amount > 0 && ` · ${fmtMoney(item.cost.refunded_amount, item.cost.currency)} refunded`}</p>}
      </div>
      {item.logistics && <p className="activity-logistics"><b>Getting there</b>{item.logistics}</p>}
      {bikeDetails.length > 0 && <dl className="bike-details">{bikeDetails.map(([label,value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>}
      {distinctNotes && <p className="activity-notes"><b>Trip note</b>{item.notes}</p>}
      <div className="activity-links">
        {item.url && <a href={item.url} target="_blank" rel="noreferrer">Official site ↗</a>}
        {item.map_url && <a href={item.map_url} target="_blank" rel="noreferrer">Google Maps ↗</a>}
        {item.user_url && <a href={item.user_url} target="_blank" rel="noreferrer">Saved link ↗</a>}
        {item.attachments?.map(file => <a key={file.id} href={file.download_url}>{file.filename}</a>)}
      </div>
      <div className="activity-plan">
        <Status value={item.selection_status} />
        <span>{item.scheduled_date ? `${fmtDate(item.scheduled_date)} · ${itineraryTime(item.scheduled_time)}` : 'No date'}</span>
        <label className="activity-select"><input type="checkbox" checked={selected} onChange={onToggle} /><span>Select</span></label>
        <div className="activity-plan-actions">
          <button type="button" className="hide-action" onClick={onVisibility} disabled={busy}>{item.selection_status === 'skipped' ? 'Restore' : 'Hide'}</button>
          <button type="button" className={managed ? 'secondary' : 'choose'} onClick={onPlan}>{item.selection_status === 'skipped' ? 'Restore or edit' : managed ? 'Edit plan' : 'Choose activity'}</button>
        </div>
        {chosen && item.scheduled_date && <a className="calendar-link" href={calendarUrl(item)} target="_blank" rel="noreferrer">Add to Google Calendar</a>}
      </div>
    </div>
  </article>
}

function ActivityModal({ item, stop, update, reload, close, onSaved, queueLabel, hasNext }) {
  const linked = item.cost || {}
  const [form, setForm] = useState({
    title: item.title, location: item.location,
    selection_status: ['shortlisted','selected','booked','done','cancelled','skipped'].includes(item.selection_status) ? item.selection_status : 'selected',
    scheduled_date: item.scheduled_date || '', scheduled_time: item.scheduled_time || '',
    estimated_cost: item.estimated_cost ?? '', actual_cost: item.actual_cost ?? '',
    payment_status: linked.payment_status || 'unknown',
    paid_amount: linked.paid_amount ?? '', paid_date: linked.paid_date || '',
    refunded_amount: linked.refunded_amount ?? '', refund_date: linked.refund_date || '',
    notes: item.notes || '', user_url: item.user_url || '',
  })
  const [file, setFile] = useState(null)
  const [saving, setSaving] = useState(false)
  const [modalError, setModalError] = useState('')
  useEffect(() => {
    const key = event => event.key === 'Escape' && close()
    addEventListener('keydown', key); return () => removeEventListener('keydown', key)
  }, [close])
  const submit = async event => {
    event.preventDefault(); setSaving(true); setModalError('')
    try {
      const needsSchedule = ['selected','booked','done'].includes(form.selection_status)
      if (needsSchedule && !form.scheduled_date) throw new Error('Choose a date for this activity. The start time can be left blank.')
      if (form.scheduled_date && stop && (form.scheduled_date < stop.date_start || form.scheduled_date > stop.date_end)) throw new Error(`${stop.name} activities must be scheduled from ${fmtDate(stop.date_start)} through ${fmtDate(stop.date_end)}.`)
      if (Number(form.refunded_amount || 0) > Number(form.paid_amount || 0)) throw new Error('Refunded amount cannot exceed the amount paid.')
      await update(item.id, {
        ...form,
        estimated_cost: form.estimated_cost === '' ? null : Number(form.estimated_cost),
        actual_cost: form.actual_cost === '' ? null : Number(form.actual_cost),
        paid_amount: form.paid_amount === '' ? 0 : Number(form.paid_amount),
        refunded_amount: form.refunded_amount === '' ? 0 : Number(form.refunded_amount),
        scheduled_date: form.scheduled_date || null,
        paid_date: form.paid_date || null,
        refund_date: form.refund_date || null,
      })
      if (file) await api.uploadAttachment(item.id, file)
      await reload(); onSaved ? onSaved() : close()
    } catch (err) { setModalError(err.message); setSaving(false) }
  }
  const archive = async () => {
    if (!confirm(`Archive “${item.title}”${item.cost ? ' and its linked budget entry' : ''}?`)) return
    setSaving(true); setModalError('')
    try { await api.deleteActivity(item.id); await reload(); close() }
    catch (err) { setModalError(err.message); setSaving(false) }
  }
  const removeAttachment = async attachment => {
    if (!confirm(`Delete ${attachment.filename}?`)) return
    setSaving(true); setModalError('')
    try { await api.deleteAttachment(attachment.id); await reload(); close() }
    catch (err) { setModalError(err.message); setSaving(false) }
  }
  const needsSchedule = ['selected','booked','done'].includes(form.selection_status)
  return <div className="modal-backdrop" onMouseDown={event => event.target === event.currentTarget && close()}>
    <form className="activity-modal" onSubmit={submit} role="dialog" aria-modal="true" aria-labelledby="activity-modal-title">
      <header><div><span>{queueLabel || 'Activity, itinerary and budget'}</span><h2 id="activity-modal-title">{item.title}</h2><p>One save updates every page.</p></div><button type="button" onClick={close} aria-label="Close">×</button></header>
      <div className="modal-grid">
        <label className="wide">Activity<input required value={form.title} onChange={e => setForm({...form,title:e.target.value})} /></label>
        <label>Status<select value={form.selection_status} onChange={e => setForm({...form,selection_status:e.target.value})}><option value="option">Not selected</option><option value="shortlisted">Shortlist only</option><option value="selected">Selected</option><option value="booked">Booked</option><option value="done">Done</option><option value="cancelled">Cancelled</option><option value="skipped">Won\u2019t do / hide</option></select></label>
        <label>Location<input value={form.location} onChange={e => setForm({...form,location:e.target.value})} /></label>
        <label>Date<input type="date" min={stop?.date_start || '2026-09-11'} max={stop?.date_end || '2026-10-15'} value={form.scheduled_date} onChange={e => setForm({...form,scheduled_date:e.target.value})} aria-required={needsSchedule} />{stop && <small>{stop.name}: {fmtDate(stop.date_start)}–{fmtDate(stop.date_end)} only</small>}</label>
        <label>Start time <small>Optional</small><input type="time" value={form.scheduled_time} onChange={e => setForm({...form,scheduled_time:e.target.value})} /></label>
        <div className="modal-divider wide"><strong>Budget</strong><span>{form.selection_status === 'cancelled' ? 'Cancelled items count only unrecovered money.' : 'Estimate is replaced by actual cost when entered.'}</span></div>
        <label>Estimate ({item.currency})<input type="number" min="0" step=".01" value={form.estimated_cost} onChange={e => setForm({...form,estimated_cost:e.target.value})} /></label>
        <label>Actual cost ({item.currency})<input type="number" min="0" step=".01" value={form.actual_cost} onChange={e => setForm({...form,actual_cost:e.target.value})} placeholder="Leave blank until known" /></label>
        <label>Payment<select value={form.payment_status} onChange={e => setForm({...form,payment_status:e.target.value})}><option value="unknown">Unknown</option><option value="pending">Pending</option><option value="partial">Part paid</option><option value="paid">Paid</option><option value="partial_refund">Part refunded</option><option value="refunded">Refunded</option></select></label>
        <label>Amount paid ({item.currency})<input type="number" min="0" step=".01" value={form.paid_amount} onChange={e => setForm({...form,paid_amount:e.target.value})} /></label>
        <label>Paid date<input type="date" value={form.paid_date} onChange={e => setForm({...form,paid_date:e.target.value})} /></label>
        <span />
        <label>Amount refunded ({item.currency})<input type="number" min="0" step=".01" value={form.refunded_amount} onChange={e => setForm({...form,refunded_amount:e.target.value})} /></label>
        <label>Refund date<input type="date" value={form.refund_date} onChange={e => setForm({...form,refund_date:e.target.value})} /></label>
        <label className="wide">Trip notes<textarea value={form.notes} onChange={e => setForm({...form,notes:e.target.value})} placeholder="Confirmation, cancellation or refund details" /></label>
        <label className="wide">Booking or reference link<input type="url" value={form.user_url} onChange={e => setForm({...form,user_url:e.target.value})} placeholder="https://…" /></label>
        <label className="wide">Attach confirmation, ticket or note<input type="file" onChange={e => setFile(e.target.files?.[0] || null)} /><small>PDF, image or document · 10 MB maximum</small></label>
      </div>
      {item.attachments?.length > 0 && <div className="existing-files"><b>Attached</b>{item.attachments.map(file => <span key={file.id}><a href={file.download_url}>{file.filename}</a><button type="button" onClick={() => removeAttachment(file)}>Delete</button></span>)}</div>}
      {modalError && <p className="modal-error">{modalError}</p>}
      <footer><button type="button" className="danger-link" onClick={archive} disabled={saving}>Archive</button><span /><button type="button" className="secondary" onClick={close}>Close</button><button className="primary" disabled={saving}>{saving ? 'Saving…' : hasNext ? 'Save & next' : form.selection_status === 'cancelled' ? 'Save cancellation' : 'Save activity'}</button></footer>
    </form>
  </div>
}

function Costs({ data, updateCost, setData, reload }) {
  const [adding, setAdding] = useState(false)
  const [draft, setDraft] = useState({ label: '', category: 'Activities', amount: '', currency: 'USD', payment_status: 'unknown' })
  const total = data.costs.reduce((sum,c) => sum + budgetImpact(c), 0)
  const gross = data.costs.reduce((sum,c) => sum + toUSD(c.amount || 0, c.currency), 0)
  const paid = data.costs.reduce((sum,c) => sum + toUSD(c.net_paid_amount || 0, c.currency), 0)
  const refunded = data.costs.reduce((sum,c) => sum + toUSD(c.refunded_amount || 0, c.currency), 0)
  const budget = data.trip.budget_usd || 0
  const categories = [...new Set(data.costs.map(c => c.category))]
  const add = async (event) => {
    event.preventDefault(); await api.createCost({ ...draft, amount: draft.amount === '' ? null : Number(draft.amount) })
    setAdding(false); setDraft({ label:'',category:'Activities',amount:'',currency:'USD',payment_status:'unknown' }); await reload()
  }
  const archive = async item => {
    const detail = item.activity_id ? ' This also archives the linked activity.' : ''
    if (!confirm(`Archive “${item.label}”?${detail}`)) return
    await api.deleteCost(item.id); await reload()
  }
  const saveBudget = async (value) => {
    const trip = await api.patchSettings({ budget_usd: Number(value) }); setData(current => ({...current, trip}))
  }
  return <div className="page costs-page">
    <PageHead title="Costs" intro="The shared ledger. Activity bookings and refunds update here automatically." actions={<button className="primary" onClick={() => setAdding(!adding)}>Add cost</button>} />
    {adding && <form className="add-form" onSubmit={add}>
      <label>Cost item<input required value={draft.label} onChange={e => setDraft({...draft,label:e.target.value})} /></label>
      <label>Category<input value={draft.category} onChange={e => setDraft({...draft,category:e.target.value})} /></label>
      <label>Currency<select value={draft.currency} onChange={e => setDraft({...draft,currency:e.target.value})}><option>USD</option><option>EUR</option></select></label>
      <label>Amount<input type="number" min="0" step=".01" value={draft.amount} onChange={e => setDraft({...draft,amount:e.target.value})} /></label>
      <label>Payment<select value={draft.payment_status} onChange={e => setDraft({...draft,payment_status:e.target.value})}>{['unknown','pending','partial','paid'].map(s => <option key={s} value={s}>{s}</option>)}</select></label>
      <button className="primary">Save cost</button>
    </form>}
    <section className="cost-headline">
      <div><span>Budget impact</span><strong>{fmtMoney(total)}</strong></div><div><span>Gross planned</span><strong>{fmtMoney(gross)}</strong></div><div><span>Net paid</span><strong>{fmtMoney(paid)}</strong></div><div><span>Refunded</span><strong>{fmtMoney(refunded)}</strong></div>
      <label>Budget (USD)<input type="number" step="500" value={budget} onChange={e => setData(current => ({...current,trip:{...current.trip,budget_usd:Number(e.target.value)}}))} onBlur={e => saveBudget(e.target.value)} /></label>
      <div className="budget-track"><i style={{width:`${Math.min(100, budget ? total/budget*100 : 0)}%`}} /><span>{budget ? Math.round(total/budget*100) : 0}% of budget</span></div>
    </section>
    {categories.map(category => <section className="cost-group" key={category}><header><h2>{category}</h2><strong>{fmtMoney(data.costs.filter(c => c.category === category).reduce((sum,c)=>sum+budgetImpact(c),0))}</strong></header>
      <div className="table-wrap"><table><thead><tr><th>Item</th><th>Booking</th><th>Payment</th><th>Paid</th><th>Refunded</th><th>Amount</th></tr></thead><tbody>
        {data.costs.filter(c => c.category === category).map(item => <tr key={item.id}>
          <td><strong>{item.url ? <a href={item.url} target="_blank" rel="noreferrer">{item.label}</a> : item.label}</strong>{item.activity_id && <span className="linked-badge">Activity</span>}{item.due_date && <small>Due {fmtDate(item.due_date)}</small>}<CostDetailsEditor item={item} save={patch => updateCost(item.id, patch)} archive={() => archive(item)} /></td>
          <td><select value={item.booking_status} onChange={e => updateCost(item.id,{booking_status:e.target.value})}><option value="booked">Booked</option><option value="estimate">Estimate</option><option value="cancelled">Cancelled</option></select></td>
          <td><select value={item.payment_status} onChange={e => updateCost(item.id,{payment_status:e.target.value})}>{['paid','partial','pending','unknown','partial_refund','refunded'].map(s => <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>)}</select></td>
          <td><MoneyInput currency={item.currency} value={item.paid_amount} save={value => updateCost(item.id,{paid_amount:value})} /></td>
          <td><MoneyInput currency={item.currency} value={item.refunded_amount} save={value => updateCost(item.id,{refunded_amount:value, payment_status:value > 0 ? (value >= item.paid_amount ? 'refunded' : 'partial_refund') : item.payment_status})} /></td>
          <td><MoneyInput currency={item.currency} value={item.amount} save={value => updateCost(item.id,{amount:value})} /></td>
        </tr>)}
      </tbody></table></div>
    </section>)}
  </div>
}

function CostDetailsEditor({ item, save, archive }) {
  const [form, setForm] = useState({
    label: item.label, category: item.category, currency: item.currency,
    paid_date: item.paid_date || '', refund_date: item.refund_date || '', due_date: item.due_date || '',
    payment_reference: item.payment_reference || '', note: item.note || '', url: item.url || '',
  })
  useEffect(() => setForm({
    label: item.label, category: item.category, currency: item.currency,
    paid_date: item.paid_date || '', refund_date: item.refund_date || '', due_date: item.due_date || '',
    payment_reference: item.payment_reference || '', note: item.note || '', url: item.url || '',
  }), [item])
  const submit = event => {
    event.preventDefault()
    save({ ...form, paid_date: form.paid_date || null, refund_date: form.refund_date || null, due_date: form.due_date || null })
  }
  return <details className="cost-editor"><summary>Edit details</summary><form onSubmit={submit}>
    <label>Label<input required value={form.label} onChange={e => setForm({...form,label:e.target.value})} /></label>
    <label>Category<input disabled={Boolean(item.activity_id)} value={form.category} onChange={e => setForm({...form,category:e.target.value})} /></label>
    <label>Currency<select value={form.currency} onChange={e => setForm({...form,currency:e.target.value})}><option>USD</option><option>EUR</option></select></label>
    <label>Due date<input type="date" value={form.due_date} onChange={e => setForm({...form,due_date:e.target.value})} /></label>
    <label>Paid date<input type="date" value={form.paid_date} onChange={e => setForm({...form,paid_date:e.target.value})} /></label>
    <label>Refund date<input type="date" value={form.refund_date} onChange={e => setForm({...form,refund_date:e.target.value})} /></label>
    <label className="wide">Reference<input value={form.payment_reference} onChange={e => setForm({...form,payment_reference:e.target.value})} /></label>
    <label className="wide">Link<input type="url" value={form.url} onChange={e => setForm({...form,url:e.target.value})} /></label>
    <label className="wide">Notes<textarea value={form.note} onChange={e => setForm({...form,note:e.target.value})} /></label>
    <div className="cost-editor-actions wide"><button type="button" className="danger-link" onClick={archive}>Archive</button><button className="secondary">Save details</button></div>
  </form></details>
}

function MoneyInput({ value, currency = 'USD', save }) {
  const [draft, setDraft] = useState(value ?? '')
  useEffect(() => setDraft(value ?? ''), [value])
  return <label className="money-input"><span>{currency === 'EUR' ? '€' : '$'}</span><input type="number" min="0" step=".01" value={draft} onChange={e => setDraft(e.target.value)} onBlur={() => save(draft === '' ? null : Number(draft))} /></label>
}

function Status({ value }) { return <span className={`status s-${value}`}>{STATUS_LABELS[value] || value}</span> }

function FatalError({ error, retry }) {
  return <main className="fatal"><h1>The trip database did not load</h1><p>{error}</p><button className="primary" onClick={retry}>Try again</button></main>
}
