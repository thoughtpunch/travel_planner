<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import Card from "primevue/card";
import Message from "primevue/message";
import { api } from "@/api/client";
import type { ShortlistItem, Trip } from "@/api/types";

const props = defineProps<{ trip: Trip }>();
const shortlist = ref<ShortlistItem[]>([]);
const runs = ref<any[]>([]);

const latestRun = computed(() => runs.value[0] || null);

onMounted(async () => {
  [shortlist.value, runs.value] = await Promise.all([
    api.listShortlist(props.trip.id),
    api.listRuns(props.trip.id),
  ]);
});
</script>

<template>
  <div class="overview-grid">
    <Card>
      <template #title>Latest run</template>
      <template #content>
        <div v-if="latestRun">
          <p>Status: <strong>{{ latestRun.status }}</strong></p>
          <p>Started {{ new Date(latestRun.started_at).toLocaleString() }}</p>
          <router-link :to="`/trips/${trip.id}/runs/${latestRun.id}`">View results →</router-link>
        </div>
        <Message v-else severity="info" :closable="false">No runs yet. Click "Run now" to fire one.</Message>
      </template>
    </Card>
    <Card>
      <template #title>Shortlist preview ({{ shortlist.length }})</template>
      <template #content>
        <div v-if="shortlist.length === 0" class="muted">Nothing saved yet.</div>
        <ul v-else>
          <li v-for="s in shortlist.slice(0, 3)" :key="s.id">
            <small>{{ s.snapshot.structure }} · {{ s.snapshot.gateway }} · ${{ s.snapshot.landed_cost?.toLocaleString() }}</small>
          </li>
        </ul>
        <router-link :to="`/trips/${trip.id}/shortlist`">Open shortlist →</router-link>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.overview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.muted { color: var(--color-muted); }
ul { padding-left: 1rem; }
</style>
