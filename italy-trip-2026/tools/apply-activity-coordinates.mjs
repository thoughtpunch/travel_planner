#!/usr/bin/env node

import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const baseUrl = String(process.env.TRIP_API_BASE || '').replace(/\/$/, '')
const username = process.env.TRIP_API_USERNAME || ''
const password = process.env.TRIP_API_PASSWORD || ''
if (!baseUrl || !username || !password) {
  throw new Error('Set TRIP_API_BASE, TRIP_API_USERNAME, and TRIP_API_PASSWORD')
}

const fixturePath = resolve(process.argv[2] || 'tools/activity-coordinates.json')
const coordinates = JSON.parse(await readFile(fixturePath, 'utf8'))
const authorization = `Basic ${Buffer.from(`${username}:${password}`).toString('base64')}`
const request = async (path, options = {}) => {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: { authorization, 'content-type': 'application/json', ...options.headers },
  })
  if (!response.ok) throw new Error(`${response.status} ${path}: ${await response.text()}`)
  return response.json()
}

const wiki = await request('/api/wiki')
const pending = wiki.activities.filter(activity => {
  const geocode = coordinates[activity.source_key]
  return geocode && (
    Number(activity.latitude) !== Number(geocode.latitude)
    || Number(activity.longitude) !== Number(geocode.longitude)
    || activity.geocode_precision !== geocode.precision
  )
})

let nextIndex = 0
let updated = 0
async function worker() {
  while (nextIndex < pending.length) {
    const activity = pending[nextIndex]
    nextIndex += 1
    const geocode = coordinates[activity.source_key]
    await request(`/api/wiki/activities/${activity.id}`, {
      method: 'PATCH',
      body: JSON.stringify({
        latitude: geocode.latitude,
        longitude: geocode.longitude,
        geocode_precision: geocode.precision,
      }),
    })
    updated += 1
    if (updated % 25 === 0) process.stdout.write(`\rUpdated ${updated}/${pending.length}`)
  }
}

await Promise.all(Array.from({ length: Math.min(8, pending.length) }, worker))
process.stdout.write(`\rUpdated ${updated}/${pending.length} activity coordinates\n`)
