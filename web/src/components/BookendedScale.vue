<script setup lang="ts">
import { computed, ref, watch } from "vue";
import Slider from "primevue/slider";
import Tag from "primevue/tag";
import InputNumber from "primevue/inputnumber";
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import AutoComplete from "primevue/autocomplete";
import Message from "primevue/message";
import type { Axis, AxisSetting, ScalePosition, StopoverTarget } from "@/api/types";

const props = defineProps<{
  axis: Axis;
  modelValue: AxisSetting;
  // Whether HARD YES is meaningful for this axis. Only stopover in v1.
  hardYesAdmitted?: boolean;
  // For HARD NO threshold-requiring axes (layover, transfer, plane_changes).
  thresholdLabel?: string;
  // Friendly axis label (rendered as <h3>, used by aria-labelledby).
  label: string;
  // Short user-facing question / hint shown under the title — without this
  // the scale is just an unlabelled slider. Recommended for every axis.
  question?: string;
  // HARD YES stopover only: the current target shape (city or sweep).
  stopoverTarget?: StopoverTarget | null;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", v: AxisSetting): void;
  (e: "update:stopoverTarget", t: StopoverTarget | null): void;
}>();

const POSITIONS: ScalePosition[] = [
  "hard_no",
  "strongly_avoid",
  "avoid",
  "neutral",
  "desire",
  "strongly_desire",
  "hard_yes",
];

const LABELS: Record<ScalePosition, string> = {
  hard_no: "HARD NO",
  strongly_avoid: "strongly avoid",
  avoid: "avoid",
  neutral: "neutral",
  desire: "desire",
  strongly_desire: "strongly desire",
  hard_yes: "HARD YES",
};

const sliderValue = ref<number>(POSITIONS.indexOf(props.modelValue.position));
const thresholdValue = ref<number | null>(
  typeof props.modelValue.threshold === "number" ? props.modelValue.threshold : null,
);
const stopoverDialogOpen = ref(false);
const stopoverCity = ref<string>(props.stopoverTarget?.city || "");
const stopoverCandidatesText = ref<string>(
  (props.stopoverTarget?.sweep_candidates || []).join(", "),
);

watch(() => props.modelValue.position, (p) => {
  sliderValue.value = POSITIONS.indexOf(p);
});

const maxPosition = computed(() =>
  props.hardYesAdmitted ? POSITIONS.length - 1 : POSITIONS.length - 2,
);

const currentLabel = computed(() => LABELS[POSITIONS[sliderValue.value]]);
const isHardNo = computed(() => POSITIONS[sliderValue.value] === "hard_no");
const isHardYes = computed(() => POSITIONS[sliderValue.value] === "hard_yes");

function emitUpdate(position: ScalePosition, threshold?: number | null) {
  emit("update:modelValue", { position, threshold: threshold ?? null });
}

function onSliderChange(v: number | number[]) {
  const idx = Array.isArray(v) ? v[0] : v;
  const clamped = Math.min(idx, maxPosition.value);
  sliderValue.value = clamped;
  const pos = POSITIONS[clamped];
  if (pos === "hard_yes" && props.axis === "stopover") {
    stopoverDialogOpen.value = true;
    return;
  }
  emitUpdate(pos, thresholdValue.value);
}

function onThresholdChange() {
  emitUpdate(POSITIONS[sliderValue.value], thresholdValue.value);
}

function confirmStopover(target: StopoverTarget) {
  emit("update:stopoverTarget", target);
  emitUpdate("hard_yes", null);
  stopoverDialogOpen.value = false;
}

function cancelStopover() {
  stopoverDialogOpen.value = false;
  // Revert to the prior position.
  sliderValue.value = POSITIONS.indexOf(props.modelValue.position);
}

function confirmNamedCity() {
  if (!stopoverCity.value.trim()) return;
  confirmStopover({ city: stopoverCity.value.trim() });
}

function confirmSweep() {
  const candidates = stopoverCandidatesText.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (candidates.length === 0) return;
  confirmStopover({ sweep_candidates: candidates });
}
</script>

<template>
  <div class="bookended-scale" :aria-labelledby="`scale-label-${props.axis}`">
    <div class="scale-title-row">
      <h3 class="scale-title" :id="`scale-label-${props.axis}`">{{ props.label }}</h3>
      <p v-if="props.question" class="scale-question">{{ props.question }}</p>
    </div>
    <div class="scale-header">
      <Tag :severity="isHardNo ? 'danger' : 'secondary'">HARD NO</Tag>
      <span class="scale-current" aria-live="polite">{{ currentLabel }}</span>
      <Tag
        v-if="props.hardYesAdmitted"
        :severity="isHardYes ? 'success' : 'secondary'"
      >HARD YES</Tag>
      <Tag
        v-else
        severity="secondary"
        class="locked-end"
        v-tooltip.top="`HARD YES is not meaningful for ${props.label} — set a HARD NO threshold instead`"
      >
        <i class="pi pi-lock" aria-hidden="true"></i> HARD YES
      </Tag>
    </div>
    <Slider
      :modelValue="sliderValue"
      :min="0"
      :max="6"
      :step="1"
      class="scale-slider"
      @change="onSliderChange"
      :aria-label="`${props.label} preference`"
      :aria-valuemin="0"
      :aria-valuemax="maxPosition"
      :aria-valuetext="currentLabel"
    />
    <div v-if="isHardNo && props.thresholdLabel" class="scale-threshold">
      <label>{{ props.thresholdLabel }}</label>
      <InputNumber
        v-model="thresholdValue"
        :min="0"
        :suffix="props.axis === 'layover_length' || props.axis === 'transfer_length' ? ' min' : ''"
        @blur="onThresholdChange"
        :aria-label="props.thresholdLabel"
      />
      <Message v-if="thresholdValue == null" severity="warn" :closable="false">
        HARD NO needs a threshold to be valid.
      </Message>
    </div>
    <div v-if="isHardYes && props.axis === 'stopover'" class="scale-stopover-summary">
      <Tag severity="success">
        <i class="pi pi-map-marker" aria-hidden="true"></i>
        <span v-if="props.stopoverTarget?.city">
          via {{ props.stopoverTarget.city }}
        </span>
        <span v-else-if="props.stopoverTarget?.sweep_candidates">
          sweep: {{ props.stopoverTarget.sweep_candidates.join(", ") }}
        </span>
      </Tag>
      <Button label="Edit" text size="small" @click="stopoverDialogOpen = true" />
    </div>

    <Dialog
      v-model:visible="stopoverDialogOpen"
      header="HARD YES stopover"
      modal
      :style="{ width: '32rem' }"
      :closable="false"
    >
      <p>
        Name a stopover city, or let the system sweep a candidate set of natural waypoints.
        The system will build legs through it and price them honestly.
      </p>
      <div class="stopover-row">
        <label>Stopover city (IATA or city name)</label>
        <InputNumber v-if="false" />
        <AutoComplete v-model="stopoverCity" :suggestions="['MAD','LIS','LHR','FRA']" />
        <Button label="Use this city" severity="primary" @click="confirmNamedCity" />
      </div>
      <div class="stopover-row">
        <label>OR sweep candidates (comma-separated IATA)</label>
        <input
          v-model="stopoverCandidatesText"
          class="p-inputtext p-component"
          placeholder="MAD, LIS, LHR, FRA"
          style="width: 100%;"
        />
        <Button label="Sweep these" severity="secondary" @click="confirmSweep" />
      </div>
      <template #footer>
        <Button label="Cancel" text @click="cancelStopover" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.bookended-scale {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1rem;
  background: var(--color-surface);
  margin-bottom: 0.75rem;
}
.scale-title-row { margin-bottom: 0.75rem; }
.scale-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}
.scale-question {
  margin: 0.25rem 0 0;
  color: var(--color-muted);
  font-size: 0.9rem;
}
.scale-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}
.scale-current {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
}
.locked-end {
  opacity: 0.55;
  cursor: not-allowed;
}
.scale-slider {
  margin: 1.25rem 0.5rem;
}
.scale-threshold {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}
.scale-stopover-summary {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.stopover-row {
  display: grid;
  gap: 0.5rem;
  margin: 0.75rem 0;
}
</style>
