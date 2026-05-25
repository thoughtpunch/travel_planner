<script setup lang="ts">
import { computed } from "vue";
import Tag from "primevue/tag";
import type { DataSource } from "@/api/types";

const props = defineProps<{ source: DataSource }>();

const palette: Record<DataSource, { label: string; severity: string; icon: string; tooltip: string }> = {
  validated_airfare: {
    label: "validated", severity: "success", icon: "pi pi-check",
    tooltip: "Confirmed at full party via SerpAPI re-query.",
  },
  transfer_table: {
    label: "table", severity: "info", icon: "pi pi-table",
    tooltip: "Hardcoded gateway-transfer table; check last_reviewed date.",
  },
  user_assumption: {
    label: "your estimate", severity: "secondary", icon: "pi pi-user",
    tooltip: "Your owned assumption — edit anytime.",
  },
  user_override: {
    label: "your override", severity: "secondary", icon: "pi pi-pencil",
    tooltip: "Your override of the table figure.",
  },
  llm_estimate_unverified: {
    label: "AI suggested — verify", severity: "warn", icon: "pi pi-sparkles",
    tooltip: "AI suggested. Treated as unverified until you confirm.",
  },
};

const entry = computed(() => palette[props.source] || palette.user_assumption);
</script>

<template>
  <Tag
    :severity="entry.severity"
    :aria-label="entry.label"
    v-tooltip.top="entry.tooltip"
  >
    <i :class="entry.icon" aria-hidden="true"></i>
    <span class="ml-1">{{ entry.label }}</span>
  </Tag>
</template>

<style scoped>
.ml-1 { margin-left: 0.25rem; font-size: 0.85em; }
</style>
