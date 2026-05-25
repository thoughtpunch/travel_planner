<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import Stepper from "primevue/stepper";
import StepList from "primevue/steplist";
import StepPanels from "primevue/steppanels";
import Step from "primevue/step";
import StepPanel from "primevue/steppanel";
import Card from "primevue/card";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Calendar from "primevue/calendar";
import Slider from "primevue/slider";
import SelectButton from "primevue/selectbutton";
import MultiSelect from "primevue/multiselect";
import Button from "primevue/button";
import Accordion from "primevue/accordion";
import AccordionPanel from "primevue/accordionpanel";
import AccordionHeader from "primevue/accordionheader";
import AccordionContent from "primevue/accordioncontent";
import Message from "primevue/message";
import { useRouter } from "vue-router";
import { api } from "@/api/client";
import type { Axis, Config, Trip } from "@/api/types";
import BookendedScale from "@/components/BookendedScale.vue";
import DataSourceTag from "@/components/DataSourceTag.vue";

const props = defineProps<{ trip: Trip }>();
const router = useRouter();

const config = ref<Config | null>(null);
const activeStep = ref(0);
const previewData = ref<Record<string, unknown> | null>(null);
const finalizing = ref(false);
const finalizeError = ref<string | null>(null);

const AXES: { axis: Axis; label: string; hardYes: boolean; threshold?: string }[] = [
  { axis: "transfer_length", label: "Transfer length", hardYes: false, threshold: "Filter out transfer longer than (min)" },
  { axis: "layover_length", label: "Layover length", hardYes: false, threshold: "Filter out any layover longer than (min)" },
  { axis: "stopover", label: "Stopover (24h+ break)", hardYes: true },
  { axis: "plane_changes", label: "Number of plane changes", hardYes: false, threshold: "Filter out more than (count)" },
  { axis: "red_eye", label: "Red-eye / pre-dawn arrival", hardYes: false },
];

const SAMPLE_GATEWAYS = ["VCE", "MXP", "LIN", "BLQ", "VRN", "TRS", "ZRH", "MUC", "FCO"];
const DC_AIRPORTS = ["IAD", "DCA", "BWI"];

onMounted(async () => {
  config.value = await api.getConfig(props.trip.config_id);
});

// Debounced PATCH on any field change.
let patchTimer: ReturnType<typeof setTimeout> | null = null;
function debouncePatch(patch: Record<string, unknown>) {
  if (patchTimer) clearTimeout(patchTimer);
  patchTimer = setTimeout(async () => {
    if (!config.value) return;
    try {
      config.value = await api.patchConfig(config.value.id, patch);
    } catch (e) {
      // Show validation errors inline.
      finalizeError.value = (e as Error).message;
    }
  }, 500);
}

function updateAxis(axis: Axis, setting: any) {
  if (!config.value) return;
  const defaults = { ...(config.value.preferences?.defaults || {}) };
  defaults[axis] = setting;
  config.value.preferences = { ...config.value.preferences, defaults };
  debouncePatch({ preferences: { defaults: { [axis]: setting } } });
}

function updateStopoverTarget(t: any) {
  if (!config.value) return;
  config.value.preferences = { ...config.value.preferences, stopover_target: t };
  debouncePatch({ preferences: { stopover_target: t } });
}

watch(() => activeStep.value, async (v) => {
  if (v === 4 && config.value) {
    try {
      previewData.value = await api.previewConfig(config.value.id);
    } catch (e) {
      previewData.value = { error: (e as Error).message };
    }
  }
});

async function finalize() {
  if (!config.value) return;
  finalizing.value = true;
  finalizeError.value = null;
  try {
    await api.finalizeConfig(config.value.id);
    const run = await api.triggerRun(config.value.id);
    router.push(`/trips/${props.trip.id}/runs/${run.id}`);
  } catch (e) {
    finalizeError.value = (e as Error).message;
  } finally {
    finalizing.value = false;
  }
}
</script>

<template>
  <div v-if="config" class="wizard">
    <Stepper :value="String(activeStep)" linear>
      <StepList>
        <Step :value="'0'" @click="activeStep = 0">Trip basics</Step>
        <Step :value="'1'" @click="activeStep = 1">Dates & legs</Step>
        <Step :value="'2'" @click="activeStep = 2">Preferences</Step>
        <Step :value="'3'" @click="activeStep = 3">Cost assumptions</Step>
        <Step :value="'4'" @click="activeStep = 4">Review & run</Step>
      </StepList>
      <StepPanels>
        <!-- Step 1: Trip basics -->
        <StepPanel :value="'0'">
          <Card>
            <template #title>Trip basics</template>
            <template #content>
              <div class="grid">
                <div class="form-row">
                  <label>Trip name</label>
                  <InputText v-model="config.name" @blur="debouncePatch({ name: config!.name })" />
                </div>
                <div class="form-row">
                  <label>Budget (party total, USD)</label>
                  <InputNumber v-model="config.budget_party_total" @blur="debouncePatch({ budget_party_total: config!.budget_party_total })" />
                </div>
                <div class="form-row">
                  <label>Adults</label>
                  <InputNumber :modelValue="config.passengers.adults" @update:modelValue="(v) => { config!.passengers.adults = v ?? 1; debouncePatch({ passengers: { adults: config!.passengers.adults } }); }" :min="1" />
                </div>
                <div class="form-row">
                  <label>Children</label>
                  <InputNumber :modelValue="config.passengers.children || 0" @update:modelValue="(v) => { config!.passengers.children = v ?? 0; debouncePatch({ passengers: { children: config!.passengers.children } }); }" :min="0" />
                </div>
              </div>
            </template>
            <template #footer>
              <Button label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activeStep = 1" />
            </template>
          </Card>
        </StepPanel>
        <!-- Step 2: Dates & legs -->
        <StepPanel :value="'1'">
          <Card>
            <template #title>Dates & legs</template>
            <template #content>
              <div v-for="leg in config.legs" :key="leg.ordinal" class="leg-card">
                <h3>Leg {{ leg.ordinal }}: {{ leg.origins.join(',') }} → {{ leg.destinations.join(',') }}</h3>
                <div class="grid">
                  <div class="form-row">
                    <label>Outbound anchor</label>
                    <InputText :modelValue="leg.date_anchor" disabled />
                  </div>
                  <div class="form-row">
                    <label>Window ± days: {{ leg.window_days }}</label>
                    <Slider :modelValue="leg.window_days" :min="0" :max="14" :step="1" disabled />
                  </div>
                  <div class="form-row">
                    <label>Destinations</label>
                    <MultiSelect :modelValue="leg.destinations" :options="SAMPLE_GATEWAYS" display="chip" disabled />
                  </div>
                </div>
              </div>
              <Message severity="info" :closable="false">
                Leg editing is read-only in this slice — modify legs via the seed/CLI for now;
                in-place editing is a follow-up.
              </Message>
            </template>
            <template #footer>
              <Button label="Back" text @click="activeStep = 0" />
              <Button label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activeStep = 2" />
            </template>
          </Card>
        </StepPanel>
        <!-- Step 3: Preferences -->
        <StepPanel :value="'2'">
          <Card>
            <template #title>Preferences</template>
            <template #subtitle>
              Bookended scales per friction axis. HARD NO filters; HARD YES (where admitted) constructs;
              soft middle reorders within the ±{{ config.preferences?.soft_band_pct || 10 }}% cost band.
            </template>
            <template #content>
              <BookendedScale
                v-for="a in AXES"
                :key="a.axis"
                :axis="a.axis"
                :label="a.label"
                :hard-yes-admitted="a.hardYes"
                :threshold-label="a.threshold"
                :modelValue="config.preferences.defaults[a.axis] || { position: 'neutral' }"
                @update:modelValue="(s) => updateAxis(a.axis, s)"
                :stopover-target="config.preferences.stopover_target"
                @update:stopoverTarget="updateStopoverTarget"
              />
              <Accordion :value="['']">
                <AccordionPanel value="overrides">
                  <AccordionHeader>Per-leg overrides (advanced)</AccordionHeader>
                  <AccordionContent>
                    <Message severity="info" :closable="false">
                      Per-leg overrides let you tighten a constraint on one leg only
                      (e.g. HARD NO red-eye on the return). Coming in a follow-up; for now
                      use global defaults.
                    </Message>
                  </AccordionContent>
                </AccordionPanel>
              </Accordion>
            </template>
            <template #footer>
              <Button label="Back" text @click="activeStep = 1" />
              <Button label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activeStep = 3" />
            </template>
          </Card>
        </StepPanel>
        <!-- Step 4: Cost assumptions -->
        <StepPanel :value="'3'">
          <Card>
            <template #title>Cost assumptions</template>
            <template #subtitle>
              Owned by you. Every value entering landed cost carries its data source tag.
            </template>
            <template #content>
              <div class="grid">
                <div class="form-row">
                  <label>Stopover lodging per night (USD)</label>
                  <InputNumber
                    :modelValue="config.cost_assumptions.stopover_lodging_per_night"
                    @update:modelValue="(v) => { config!.cost_assumptions.stopover_lodging_per_night = v ?? 0; debouncePatch({ cost_assumptions: { stopover_lodging_per_night: v }}); }"
                    :min="0"
                    prefix="$"
                  />
                  <DataSourceTag
                    :source="config.cost_assumptions.llm_suggested?.stopover_lodging_per_night ? 'llm_estimate_unverified' : 'user_assumption'"
                  />
                </div>
                <div class="form-row">
                  <label>Rooms (for forced/intentional overnight)</label>
                  <InputNumber
                    :modelValue="config.cost_assumptions.stopover_rooms"
                    @update:modelValue="(v) => { config!.cost_assumptions.stopover_rooms = v ?? 1; debouncePatch({ cost_assumptions: { stopover_rooms: v }}); }"
                    :min="1"
                  />
                </div>
              </div>
            </template>
            <template #footer>
              <Button label="Back" text @click="activeStep = 2" />
              <Button label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activeStep = 4" />
            </template>
          </Card>
        </StepPanel>
        <!-- Step 5: Review -->
        <StepPanel :value="'4'">
          <Card>
            <template #title>Review & run</template>
            <template #content>
              <div v-if="previewData" class="preview-grid">
                <div class="metric">
                  <strong>Matrix size</strong>
                  <span class="big-number">{{ previewData.matrix_size }}</span>
                  <small>total fare queries (incl. {{ previewData.stopover_matrix_size || 0 }} from constructed stopovers)</small>
                </div>
                <div class="metric">
                  <strong>SerpAPI floor</strong>
                  <span class="big-number">{{ previewData.planned_serpapi_calls }}</span>
                  <small>validation calls — the actual count may be higher if scraper fallback fires</small>
                </div>
                <div class="metric">
                  <strong>Constructed stopovers</strong>
                  <span class="big-number">{{ previewData.constructed_stopover_count }}</span>
                  <small>built by HARD YES on stopover</small>
                </div>
              </div>
              <Message v-if="finalizeError" severity="error">{{ finalizeError }}</Message>
            </template>
            <template #footer>
              <Button label="Back" text @click="activeStep = 3" />
              <Button label="Run now" icon="pi pi-play" severity="primary" :loading="finalizing" @click="finalize" />
            </template>
          </Card>
        </StepPanel>
      </StepPanels>
    </Stepper>
  </div>
</template>

<style scoped>
.wizard { max-width: 900px; margin: 0 auto; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin: 0.5rem 0;
}
.form-row { display: grid; gap: 0.25rem; }
.form-row label { font-size: 0.9em; color: var(--color-muted); }
.leg-card {
  border-left: 3px solid var(--color-border);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
}
.leg-card h3 { margin: 0 0 0.5rem; }
.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.metric {
  display: grid; gap: 0.25rem;
  padding: 1rem;
  background: var(--color-bg);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
}
.big-number { font-size: 2rem; font-weight: 600; }
.metric small { color: var(--color-muted); }
</style>
