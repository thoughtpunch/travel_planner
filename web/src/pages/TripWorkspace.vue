<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import TabMenu from "primevue/tabmenu";
import Inplace from "primevue/inplace";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useTripsStore } from "@/stores/trips";
import { api } from "@/api/client";
import type { Trip } from "@/api/types";

const props = defineProps<{ id: string }>();
const route = useRoute();
const router = useRouter();
const trips = useTripsStore();

const trip = ref<Trip | null>(null);
const running = ref(false);

const tabs = ref([
  { label: "Overview", icon: "pi pi-home", to: `/trips/${props.id}/overview` },
  { label: "Wizard", icon: "pi pi-list", to: `/trips/${props.id}/wizard` },
  { label: "Runs", icon: "pi pi-history", to: `/trips/${props.id}/runs` },
  { label: "Shortlist", icon: "pi pi-bookmark", to: `/trips/${props.id}/shortlist` },
  { label: "Notes", icon: "pi pi-pencil", to: `/trips/${props.id}/notes` },
]);

onMounted(async () => {
  trip.value = await api.getTrip(Number(props.id));
});

async function renameTrip(newName: string) {
  if (!trip.value || !newName.trim()) return;
  trip.value = await trips.patch(trip.value.id, { name: newName.trim() });
}

async function runNow() {
  if (!trip.value) return;
  running.value = true;
  try {
    const run = await api.triggerRun(trip.value.config_id);
    router.push(`/trips/${trip.value.id}/runs/${run.id}`);
  } finally {
    running.value = false;
  }
}
</script>

<template>
  <section v-if="trip">
    <header class="workspace-header">
      <div>
        <Inplace>
          <template #display>
            <h1 class="trip-title">{{ trip.name }} <i class="pi pi-pencil tiny" aria-hidden="true"></i></h1>
          </template>
          <template #content="{ closeCallback }">
            <InputText v-model="trip.name" @keydown.enter="renameTrip(trip!.name); closeCallback()" />
          </template>
        </Inplace>
        <p class="trip-meta">Config #{{ trip.config_id }} · created {{ new Date(trip.created_at).toLocaleDateString() }}</p>
      </div>
      <Button
        label="Run now"
        icon="pi pi-play"
        severity="primary"
        :loading="running"
        @click="runNow"
      />
    </header>
    <TabMenu :model="tabs" :activeIndex="tabs.findIndex((t) => t.to === route.path)" />
    <div class="tab-content">
      <router-view :trip="trip" />
    </div>
  </section>
</template>

<style scoped>
.workspace-header {
  display: flex; justify-content: space-between; align-items: center;
  margin: 1rem 0;
}
.trip-title { margin: 0; }
.tiny { font-size: 0.6em; opacity: 0.5; }
.trip-meta { color: var(--color-muted); margin: 0.25rem 0 0; }
.tab-content { margin-top: 1rem; }
</style>
