<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Card from "primevue/card";
import Knob from "primevue/knob";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import ProgressBar from "primevue/progressbar";
import Skeleton from "primevue/skeleton";
import Message from "primevue/message";
import Button from "primevue/button";
import Timeline from "primevue/timeline";
import { useToast } from "primevue/usetoast";
import { api } from "@/api/client";
import type { Itinerary, RunResults } from "@/api/types";
import StatusBadge from "@/components/StatusBadge.vue";
import FrictionChip from "@/components/FrictionChip.vue";
import RankDeltaBadge from "@/components/RankDeltaBadge.vue";
import DataSourceTag from "@/components/DataSourceTag.vue";

const props = defineProps<{ id: string; runId: string }>();
const router = useRouter();
const toast = useToast();

const results = ref<RunResults | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const selectedItin = ref<Itinerary | null>(null);
const softBandPct = ref(10);
const status = ref<string>("PENDING");
const stage = ref<string>("pending");

// SSE bookkeeping
let eventSource: EventSource | null = null;
let pollTimer: ReturnType<typeof setInterval> | null = null;
let sseReconnectAttempts = 0;

const cheapestValidated = computed(() => {
  if (!results.value) return null;
  const validated = results.value.itineraries.filter(
    (it) => it.verification_status === "VALIDATED" && it.landed_cost != null,
  );
  if (validated.length === 0) return null;
  return Math.min(...validated.map((it) => it.landed_cost!));
});

const reorderedItineraries = computed<Itinerary[]>(() => {
  if (!results.value) return [];
  const base = results.value.itineraries.slice();
  const cheapest = cheapestValidated.value;
  if (!cheapest) return base;
  const band = cheapest * (1 + softBandPct.value / 100);
  // Re-sort: inside band, allow soft-delta to nudge; outside, cost wins.
  return base.sort((a, b) => {
    const ac = a.landed_cost ?? Number.POSITIVE_INFINITY;
    const bc = b.landed_cost ?? Number.POSITIVE_INFINITY;
    const ainband = ac <= band;
    const binband = bc <= band;
    if (ainband && binband) {
      const ad = a.preference_explanations.reduce((s, e) => s + e.rank_delta, 0);
      const bd = b.preference_explanations.reduce((s, e) => s + e.rank_delta, 0);
      // higher delta wins → smaller key
      return (ac - bd * 5 * cheapest / 100) - (bc - ad * 5 * cheapest / 100);
    }
    return ac - bc;
  });
});

function startSSE() {
  if (eventSource) return;
  try {
    eventSource = new EventSource(`/api/runs/${props.runId}/stream`);
    eventSource.addEventListener("status", (e) => {
      const d = JSON.parse((e as MessageEvent).data);
      status.value = d.status;
      stage.value = d.stage;
    });
    eventSource.addEventListener("scoring_complete", () => {
      fetchResults();
    });
    eventSource.addEventListener("error", () => {
      sseReconnectAttempts++;
      if (sseReconnectAttempts >= 3) {
        toast.add({
          severity: "warn",
          summary: "Live stream dropped",
          detail: "Falling back to 2s polling.",
          life: 4000,
        });
        eventSource?.close();
        eventSource = null;
        startPolling();
      }
    });
  } catch (e) {
    startPolling();
  }
}

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(async () => {
    const r = await api.runResults(Number(props.runId));
    results.value = r;
    status.value = r.run.status;
    if (r.run.status === "COMPLETE" || r.run.status === "FAILED") {
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = null;
    }
  }, 2000);
}

async function fetchResults() {
  try {
    const r = await api.runResults(Number(props.runId));
    results.value = r;
    status.value = r.run.status;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchResults();
  if (status.value === "RUNNING" || status.value === "PENDING") {
    startSSE();
  }
});

onUnmounted(() => {
  if (eventSource) eventSource.close();
  if (pollTimer) clearInterval(pollTimer);
});

async function saveToShortlist(itin: Itinerary) {
  if (!results.value) return;
  try {
    await api.addToShortlist(Number(props.id), results.value.run.id, itin.id);
    toast.add({ severity: "success", summary: "Saved to shortlist", life: 3000 });
  } catch (e) {
    toast.add({ severity: "error", summary: "Save failed", detail: (e as Error).message, life: 5000 });
  }
}

function exportCsv() {
  if (!results.value) return;
  const headers = ["rank", "status", "structure", "gateway", "landed_cost", "stops", "red_eye", "stopover_city"];
  const rows = reorderedItineraries.value.map((it) => [
    it.rank,
    it.verification_status,
    it.structure,
    it.gateway || "",
    it.landed_cost ?? "",
    it.friction_attributes?.plane_changes ?? "",
    it.friction_attributes?.red_eye ? "yes" : "no",
    it.friction_attributes?.stopover_city || "",
  ]);
  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `trip_${props.id}_run_${props.runId}.csv`;
  a.click();
}
</script>

<template>
  <section>
    <header class="results-header">
      <Button icon="pi pi-arrow-left" text @click="router.push(`/trips/${props.id}/runs`)" aria-label="back to runs" />
      <h2>Run #{{ props.runId }}</h2>
      <StatusBadge :status="status" />
    </header>

    <ProgressBar
      v-if="status !== 'COMPLETE' && status !== 'FAILED'"
      mode="indeterminate"
      style="height: 6px"
      :aria-label="`stage: ${stage}`"
    />

    <div v-if="error">
      <Message severity="error">{{ error }}</Message>
    </div>

    <div v-else-if="loading">
      <Skeleton height="120px" />
    </div>

    <div v-else-if="results">
      <Card class="spine-card">
        <template #title>Cost spine</template>
        <template #content>
          <div class="spine-grid">
            <div class="spine-metric">
              <small>Cheapest VALIDATED landed cost</small>
              <strong class="big-number">
                {{ cheapestValidated != null ? `$${cheapestValidated.toLocaleString()}` : "—" }}
              </strong>
            </div>
            <div class="spine-metric">
              <small>Scraper calls</small>
              <strong>{{ results.run.scraper_calls }}</strong>
            </div>
            <div class="spine-metric">
              <small>SerpAPI calls</small>
              <strong>{{ results.run.serpapi_calls }}</strong>
            </div>
            <div class="spine-metric soft-band">
              <small>Soft band ±%</small>
              <Knob v-model="softBandPct" :min="0" :max="30" :step="1" :size="80" />
              <Message severity="info" :closable="false" class="band-hint">
                Live preview — re-run to persist this band.
              </Message>
            </div>
          </div>
        </template>
      </Card>

      <Splitter style="height: calc(100vh - 320px);" class="results-splitter">
        <SplitterPanel :size="60" :minSize="30">
          <div class="table-toolbar">
            <Button label="Export CSV" icon="pi pi-download" outlined @click="exportCsv" size="small" />
          </div>
          <DataTable
            :value="reorderedItineraries"
            v-model:selection="selectedItin"
            selectionMode="single"
            dataKey="id"
            sortMode="multiple"
            removableSort
            stripedRows
            scrollable
            scrollHeight="flex"
            tableStyle="min-width: 60rem"
          >
            <Column field="rank" header="#" sortable frozen style="width: 4rem" />
            <Column field="verification_status" header="Status" sortable filter>
              <template #body="{ data }"><StatusBadge :status="data.verification_status" /></template>
            </Column>
            <Column field="structure" header="Structure" sortable />
            <Column field="gateway" header="Gateway" sortable>
              <template #body="{ data }">
                {{ data.gateway }}
                <small v-if="data.friction_attributes?.stopover_city"> via {{ data.friction_attributes.stopover_city }}</small>
              </template>
            </Column>
            <Column field="landed_cost" header="Landed cost" sortable frozen alignFrozen="right">
              <template #body="{ data }">
                <strong v-if="data.landed_cost != null">${{ data.landed_cost.toLocaleString() }}</strong>
                <span v-else class="muted">—</span>
              </template>
            </Column>
            <Column header="Components">
              <template #body="{ data }">
                <div v-if="data.cost_breakdown" class="component-stack">
                  <span v-for="c in data.cost_breakdown.components" :key="c.label" class="component-line">
                    <small>{{ c.label }}: ${{ c.total.toLocaleString() }}</small>
                    <DataSourceTag :source="c.data_source" />
                  </span>
                </div>
              </template>
            </Column>
            <Column header="Friction">
              <template #body="{ data }">
                <div class="friction-stack" v-if="data.friction_attributes">
                  <FrictionChip axis="plane_changes" :value="data.friction_attributes.plane_changes" />
                  <FrictionChip axis="layover_length" :value="data.friction_attributes.layover_minutes_max" />
                  <FrictionChip axis="red_eye" :value="data.friction_attributes.red_eye" />
                  <FrictionChip axis="stopover" :value="data.friction_attributes.stopover_city" />
                </div>
              </template>
            </Column>
            <Column header="Δ rank">
              <template #body="{ data }">
                <RankDeltaBadge
                  :delta="data.preference_explanations.reduce((s: number, e: any) => s + e.rank_delta, 0)"
                  :reason="data.preference_explanations.map((e: any) => e.reason).join('; ')"
                />
              </template>
            </Column>
            <Column header="" style="width: 4rem">
              <template #body="{ data }">
                <Button
                  icon="pi pi-bookmark"
                  size="small"
                  text
                  rounded
                  aria-label="save to shortlist"
                  @click.stop="saveToShortlist(data)"
                />
              </template>
            </Column>
          </DataTable>
        </SplitterPanel>
        <SplitterPanel :size="40" :minSize="20">
          <Card v-if="selectedItin" class="detail-card">
            <template #title>Detail · rank #{{ selectedItin.rank }}</template>
            <template #content>
              <h4>Cost breakdown</h4>
              <ul v-if="selectedItin.cost_breakdown" class="breakdown">
                <li v-for="c in selectedItin.cost_breakdown.components" :key="c.label">
                  <strong>{{ c.label }}</strong>: ${{ c.total.toLocaleString() }}
                  <DataSourceTag :source="c.data_source" />
                </li>
                <li><strong>Total</strong>: ${{ selectedItin.cost_breakdown.total.toLocaleString() }}</li>
              </ul>
              <h4>Legs</h4>
              <Timeline :value="selectedItin.fares" align="left">
                <template #content="{ item }">
                  {{ item.origin }} → {{ item.destination }}
                  <small>· {{ item.date }} · {{ item.carrier }} · ${{ item.price_per_pax }}/pax</small>
                </template>
              </Timeline>
              <h4>Preference explanations</h4>
              <ul v-if="selectedItin.preference_explanations.length">
                <li v-for="e in selectedItin.preference_explanations" :key="e.axis + e.direction">
                  <strong>{{ e.axis }}</strong>: {{ e.direction }} ({{ e.rank_delta > 0 ? "+" : "" }}{{ e.rank_delta }}) — {{ e.reason }}
                </li>
              </ul>
              <p v-else class="muted">No preference effects on this itinerary.</p>
            </template>
          </Card>
          <Message v-else severity="info" :closable="false">
            Select a row to see the cost breakdown, leg timeline, and preference explanations.
          </Message>
        </SplitterPanel>
      </Splitter>
    </div>
  </section>
</template>

<style scoped>
.results-header {
  display: flex; gap: 0.75rem; align-items: center; margin: 0.5rem 0 1rem;
}
.results-header h2 { margin: 0; }
.spine-card { margin-bottom: 1rem; }
.spine-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;
}
.spine-metric { display: grid; gap: 0.25rem; }
.spine-metric.soft-band { gap: 0.5rem; }
.big-number { font-size: 1.75rem; font-weight: 600; }
.muted { color: var(--color-muted); }
.results-splitter { border: 1px solid var(--color-border); border-radius: var(--radius); }
.table-toolbar { padding: 0.5rem; border-bottom: 1px solid var(--color-border); }
.component-stack { display: grid; gap: 0.15rem; }
.component-line { display: flex; gap: 0.4rem; align-items: center; }
.friction-stack { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.detail-card { height: 100%; overflow: auto; }
.breakdown { list-style: none; padding: 0; }
.breakdown li { margin: 0.25rem 0; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.band-hint { font-size: 0.8em; padding: 0.25rem 0.5rem; }
</style>
