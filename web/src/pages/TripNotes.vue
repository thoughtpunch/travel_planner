<script setup lang="ts">
import { ref, watch } from "vue";
import Textarea from "primevue/textarea";
import { useTripsStore } from "@/stores/trips";
import type { Trip } from "@/api/types";

const props = defineProps<{ trip: Trip }>();
const trips = useTripsStore();
const notes = ref(props.trip.notes || "");

let timer: ReturnType<typeof setTimeout> | null = null;
watch(notes, (v) => {
  if (timer) clearTimeout(timer);
  timer = setTimeout(() => trips.patch(props.trip.id, { notes: v }), 1000);
});
</script>

<template>
  <Textarea
    v-model="notes"
    rows="20"
    placeholder="Free-form notes for this trip — autosaves."
    autoResize
    style="width: 100%"
  />
</template>
