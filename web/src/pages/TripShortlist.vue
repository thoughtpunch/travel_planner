<script setup lang="ts">
import { onMounted, ref } from "vue";
import DataView from "primevue/dataview";
import Card from "primevue/card";
import Button from "primevue/button";
import Textarea from "primevue/textarea";
import Chip from "primevue/chip";
import Message from "primevue/message";
import { api } from "@/api/client";
import type { ShortlistItem, Trip } from "@/api/types";

const props = defineProps<{ trip: Trip }>();
const items = ref<ShortlistItem[]>([]);

onMounted(async () => { items.value = await api.listShortlist(props.trip.id); });

async function updateNotes(item: ShortlistItem) {
  await api.patchShortlistItem(props.trip.id, item.id, { notes: item.notes });
}

async function removeItem(item: ShortlistItem) {
  await api.deleteShortlistItem(props.trip.id, item.id);
  items.value = items.value.filter((i) => i.id !== item.id);
}
</script>

<template>
  <Message v-if="items.length === 0" severity="info" :closable="false">
    Save itineraries from a run results page (bookmark icon) to build a shortlist.
  </Message>
  <DataView v-else :value="items">
    <template #list="slot">
      <div class="shortlist">
        <Card v-for="item in slot.items" :key="item.id" class="shortlist-card">
          <template #title>
            {{ item.snapshot.structure }} · {{ item.snapshot.gateway }}
            <Chip v-for="t in item.tags" :key="t" :label="t" />
          </template>
          <template #subtitle>
            <strong>${{ item.snapshot.landed_cost?.toLocaleString() }}</strong>
            · saved from run #{{ item.run_id }} ·
            {{ new Date(item.created_at).toLocaleDateString() }}
          </template>
          <template #content>
            <Textarea
              v-model="item.notes"
              rows="2"
              placeholder="Notes — why this option?"
              @blur="updateNotes(item)"
              autoResize
              class="w-full"
            />
          </template>
          <template #footer>
            <Button label="Remove" icon="pi pi-trash" severity="danger" text size="small" @click="removeItem(item)" />
          </template>
        </Card>
      </div>
    </template>
  </DataView>
</template>

<style scoped>
.shortlist { display: grid; gap: 0.5rem; padding: 0.5rem 0; }
.shortlist-card { background: var(--color-surface); }
.w-full { width: 100%; }
</style>
