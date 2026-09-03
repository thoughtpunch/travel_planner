async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `Request failed (${response.status})`)
  }
  return response.json()
}

export const api = {
  load: () => request('/api/wiki'),
  patchActivity: (id, patch) => request(`/api/wiki/activities/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  patchActivitiesBulk: (ids, action) => request('/api/wiki/activities/bulk', {
    method: 'PATCH', body: JSON.stringify({ ids, action }),
  }),
  createActivity: (payload) => request('/api/wiki/activities', {
    method: 'POST', body: JSON.stringify(payload),
  }),
  deleteActivity: id => request(`/api/wiki/activities/${id}`, { method: 'DELETE' }),
  uploadAttachment: async (id, file) => {
    const form = new FormData()
    form.append('attachment', file)
    const response = await fetch(`/api/wiki/activities/${id}/attachments`, { method: 'POST', body: form })
    if (!response.ok) throw new Error(await response.text() || `Upload failed (${response.status})`)
    return response.json()
  },
  deleteAttachment: id => request(`/api/wiki/attachments/${id}`, { method: 'DELETE' }),
  patchCost: (id, patch) => request(`/api/wiki/costs/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  createCost: (payload) => request('/api/wiki/costs', {
    method: 'POST', body: JSON.stringify(payload),
  }),
  deleteCost: id => request(`/api/wiki/costs/${id}`, { method: 'DELETE' }),
  patchSettings: (patch) => request('/api/wiki/settings', {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  patchLeg: (id, patch) => request(`/api/wiki/legs/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  patchStay: (id, patch) => request(`/api/wiki/stays/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  patchDay: (id, patch) => request(`/api/wiki/days/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  createItineraryItem: payload => request('/api/wiki/itinerary-items', {
    method: 'POST', body: JSON.stringify(payload),
  }),
  patchItineraryItem: (id, patch) => request(`/api/wiki/itinerary-items/${id}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  }),
  deleteItineraryItem: id => request(`/api/wiki/itinerary-items/${id}`, { method: 'DELETE' }),
}
