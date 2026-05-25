import type {
  Config,
  CopilotResponse,
  Run,
  RunResults,
  ShortlistItem,
  Trip,
} from "./types";

const BASE = "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  // Trips
  listTrips: (includeDeleted = false) =>
    req<Trip[]>(`/trips${includeDeleted ? "?include_deleted=true" : ""}`),
  createTrip: (body: { name: string; config_id?: number; notes?: string }) =>
    req<Trip>("/trips", { method: "POST", body: JSON.stringify(body) }),
  getTrip: (id: number) => req<Trip>(`/trips/${id}`),
  patchTrip: (id: number, patch: { name?: string; notes?: string }) =>
    req<Trip>(`/trips/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deleteTrip: (id: number) => req<void>(`/trips/${id}`, { method: "DELETE" }),

  // Shortlist
  listShortlist: (tripId: number) => req<ShortlistItem[]>(`/trips/${tripId}/shortlist`),
  addToShortlist: (tripId: number, runId: number, itineraryId: number) =>
    req<ShortlistItem>(`/trips/${tripId}/shortlist`, {
      method: "POST",
      body: JSON.stringify({ run_id: runId, itinerary_id: itineraryId }),
    }),
  patchShortlistItem: (
    tripId: number,
    itemId: number,
    patch: { notes?: string; tags?: string[]; order_index?: number },
  ) =>
    req<ShortlistItem>(`/trips/${tripId}/shortlist/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),
  deleteShortlistItem: (tripId: number, itemId: number) =>
    req<void>(`/trips/${tripId}/shortlist/${itemId}`, { method: "DELETE" }),

  // Configs
  getConfig: (id: number) => req<Config>(`/configs/${id}`),
  patchConfig: (id: number, patch: Record<string, unknown>) =>
    req<Config>(`/configs/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  previewConfig: (id: number) =>
    req<Record<string, unknown>>(`/configs/${id}/preview`),
  finalizeConfig: (id: number) =>
    req<Config>(`/configs/${id}/finalize`, { method: "POST" }),

  // Runs
  listRuns: (tripId: number) =>
    req<Run[]>(`/trips/${tripId}/runs`),
  triggerRun: (configId: number) =>
    req<Run>(`/runs?config_id=${configId}`, { method: "POST" }),
  runResults: (runId: number) => req<RunResults>(`/runs/${runId}/results`),

  // Copilot
  suggestPreferences: (natural_language: string) =>
    req<CopilotResponse>("/copilot/preferences/suggest", {
      method: "POST",
      body: JSON.stringify({ natural_language }),
    }),
  suggestCostAssumptions: (trip_context: Record<string, unknown>) =>
    req<CopilotResponse>("/copilot/cost_assumptions/suggest", {
      method: "POST",
      body: JSON.stringify({ trip_context }),
    }),
  suggestStopoverWaypoints: (origin: string, destination_gateways: string[]) =>
    req<{ candidates: string[]; rationale: string }>(
      "/copilot/stopover_waypoints/suggest",
      {
        method: "POST",
        body: JSON.stringify({ origin, destination_gateways }),
      },
    ),
};
