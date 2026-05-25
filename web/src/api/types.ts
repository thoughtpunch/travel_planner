// Types mirror the FastAPI schemas. Hand-written for v1; in v2 generate
// from FastAPI's OpenAPI schema via openapi-typescript.

export type Axis =
  | "transfer_length"
  | "layover_length"
  | "stopover"
  | "plane_changes"
  | "red_eye";

export type ScalePosition =
  | "hard_no"
  | "strongly_avoid"
  | "avoid"
  | "neutral"
  | "desire"
  | "strongly_desire"
  | "hard_yes";

export type DataSource =
  | "validated_airfare"
  | "transfer_table"
  | "user_assumption"
  | "user_override"
  | "llm_estimate_unverified";

export interface AxisSetting {
  position: ScalePosition;
  threshold?: number | Record<string, unknown> | null;
}

export interface PerLegOverride {
  leg_ordinal: number;
  axis: Axis;
  position: ScalePosition;
  threshold?: number | Record<string, unknown> | null;
}

export interface StopoverTarget {
  city?: string | null;
  sweep_candidates?: string[] | null;
}

export interface Preferences {
  defaults: Partial<Record<Axis, AxisSetting>>;
  per_leg_overrides: PerLegOverride[];
  stopover_target?: StopoverTarget | null;
  soft_band_pct: number;
}

export interface TransferOverride {
  gateway: string;
  mode: "rail" | "ferry" | "bus" | "drive";
  per_person_cost: number;
}

export interface CostAssumptions {
  stopover_lodging_per_night: number;
  stopover_rooms: number;
  transfer_overrides: TransferOverride[];
  llm_suggested: Record<string, boolean>;
}

export interface CostComponent {
  label: string;
  per_person_amount: number | null;
  party_multiplier: number;
  total: number;
  currency: string;
  data_source: DataSource;
  user_overridable: boolean;
  metadata: Record<string, unknown>;
  original_table_value: number | null;
}

export interface LandedCost {
  total: number;
  currency: string;
  components: CostComponent[];
  forces_overnight: boolean;
}

export interface FrictionAttributes {
  transfer_minutes: number;
  layover_minutes_max: number;
  layover_minutes_total: number;
  plane_changes: number;
  red_eye: boolean;
  has_stopover: boolean;
  stopover_city: string | null;
  forces_overnight: boolean;
}

export interface PreferenceExplanation {
  axis: Axis;
  direction: "filter_match" | "construct" | "desire_match" | "avoid_match" | "neutral";
  rank_delta: number;
  reason: string;
}

export interface Leg {
  ordinal: number;
  origins: string[];
  destinations: string[];
  date_anchor: string;
  window_days: number;
  sampling_strategy: string;
  return_date_anchor?: string | null;
  return_window_days?: number | null;
  return_sampling_strategy?: string | null;
}

export interface Config {
  id: number;
  name: string;
  budget_party_total: number;
  currency: string;
  passengers: Record<string, number>;
  structures: string[];
  blackout_ranges: Array<Record<string, string>>;
  validation_tolerance_pct: number;
  validation_top_n: number;
  envelope_long_gap_days: number;
  preferences: Preferences;
  cost_assumptions: CostAssumptions;
  legs: Leg[];
  created_at: string;
  updated_at: string;
}

export interface Trip {
  id: number;
  name: string;
  config_id: number;
  notes: string;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Run {
  id: number;
  config_id: number;
  status: "PENDING" | "RUNNING" | "COMPLETE" | "FAILED";
  started_at: string;
  finished_at: string | null;
  scraper_calls: number;
  serpapi_calls: number;
  serpapi_quota_remaining: number | null;
  error: string | null;
}

export interface Fare {
  id: number;
  leg_ordinal: number;
  structure: string;
  origin: string;
  destination: string;
  date: string;
  return_date: string | null;
  carrier: string;
  price_per_pax: number;
  price_party: number;
  currency: string;
  stops: number;
  duration_minutes: number;
  source: string;
  verification_status: string;
  fetched_at: string;
}

export interface Itinerary {
  id: number;
  structure: string;
  total_party_price: number;
  currency: string;
  verification_status: string;
  gateway: string | null;
  train_to_venice: Record<string, unknown> | null;
  flags: string[];
  rank: number;
  fares: Fare[];
  landed_cost: number | null;
  cost_breakdown: LandedCost | null;
  friction_attributes: FrictionAttributes | null;
  preference_explanations: PreferenceExplanation[];
}

export interface RunResults {
  run: Run;
  itineraries: Itinerary[];
  budget_verdict: Record<string, unknown>;
  quota: Record<string, unknown>;
  structures: Record<string, string>;
  failed_query_count: number;
  failed_fares: unknown[];
  filtered_out_count_by_axis: Partial<Record<Axis, number>>;
}

export interface ShortlistItem {
  id: number;
  trip_id: number;
  run_id: number;
  itinerary_id: number;
  snapshot: Record<string, unknown>;
  notes: string;
  tags: string[];
  order_index: number;
  created_at: string;
}

export interface CopilotSuggestion {
  path: string;
  value: unknown;
  confidence: number;
  rationale: string;
  unverified: boolean;
}

export interface CopilotResponse {
  suggestions: CopilotSuggestion[];
}
