<script setup lang="ts">
import { computed } from "vue";
import Tag from "primevue/tag";

const props = defineProps<{ status: string }>();

const palette: Record<string, { severity: string; icon: string; label: string }> = {
  VALIDATED: { severity: "success", icon: "pi pi-check-circle", label: "Validated" },
  LEAD: { severity: "warn", icon: "pi pi-info-circle", label: "Lead" },
  VALIDATION_FAILED: { severity: "danger", icon: "pi pi-times-circle", label: "Validation failed" },
  STALE: { severity: "contrast", icon: "pi pi-clock", label: "Stale" },
  SKIPPED_QUOTA: { severity: "warn", icon: "pi pi-pause", label: "Quota skipped" },
  FAILED: { severity: "danger", icon: "pi pi-exclamation-triangle", label: "Failed" },
  BLACKOUT: { severity: "secondary", icon: "pi pi-ban", label: "Blackout" },
  LONG_GAP: { severity: "secondary", icon: "pi pi-arrows-h", label: "Long gap" },
  INCOMPLETE: { severity: "warn", icon: "pi pi-question-circle", label: "Incomplete" },
};

const entry = computed(
  () => palette[props.status] || { severity: "secondary", icon: "pi pi-tag", label: props.status },
);
</script>

<template>
  <Tag :severity="entry.severity" :aria-label="entry.label">
    <i :class="entry.icon" aria-hidden="true"></i>
    <span class="ml-1">{{ entry.label }}</span>
  </Tag>
</template>

<style scoped>
.ml-1 { margin-left: 0.25rem; }
</style>
