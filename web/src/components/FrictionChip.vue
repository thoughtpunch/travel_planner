<script setup lang="ts">
import { computed } from "vue";
import Chip from "primevue/chip";
import type { Axis } from "@/api/types";

const props = defineProps<{
  axis: Axis;
  value: number | boolean | string | null;
}>();

const label = computed(() => {
  switch (props.axis) {
    case "layover_length": {
      const m = Number(props.value || 0);
      if (m <= 0) return "no layover";
      return `layover ${Math.floor(m / 60)}h ${m % 60}m`;
    }
    case "transfer_length": {
      const m = Number(props.value || 0);
      return `transfer ${Math.floor(m / 60)}h ${m % 60}m`;
    }
    case "plane_changes": {
      const n = Number(props.value || 0);
      return n === 0 ? "non-stop" : `${n} stop${n === 1 ? "" : "s"}`;
    }
    case "red_eye":
      return props.value ? "red-eye" : "";
    case "stopover":
      return props.value ? `stopover ${props.value}` : "";
    default:
      return String(props.value || "");
  }
});

const icon = computed(() => {
  switch (props.axis) {
    case "red_eye": return "pi pi-moon";
    case "stopover": return "pi pi-map-marker";
    case "plane_changes": return "pi pi-send";
    case "layover_length": return "pi pi-clock";
    case "transfer_length": return "pi pi-car";
    default: return "pi pi-tag";
  }
});
</script>

<template>
  <Chip v-if="label" :label="label" :icon="icon" />
</template>
