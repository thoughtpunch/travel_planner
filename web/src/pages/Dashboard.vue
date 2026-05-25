<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import DataView from "primevue/dataview";
import Card from "primevue/card";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Message from "primevue/message";
import { useTripsStore } from "@/stores/trips";

const router = useRouter();
const trips = useTripsStore();
const showCreate = ref(false);
const newName = ref("");
const layout = ref<"grid" | "list">("grid");

onMounted(() => trips.fetchAll());

async function createAndOpen() {
  if (!newName.value.trim()) return;
  const t = await trips.create({ name: newName.value.trim() });
  showCreate.value = false;
  newName.value = "";
  router.push(`/trips/${t.id}/wizard`);
}
</script>

<template>
  <section>
    <header class="dashboard-header">
      <h1>Your trips</h1>
      <div>
        <Button
          label="New trip"
          icon="pi pi-plus"
          severity="primary"
          @click="showCreate = true"
        />
      </div>
    </header>

    <Message v-if="trips.trips.length === 0 && !trips.loading" :closable="false" severity="info">
      No trips yet. A "trip" is a config + many runs + a saved-itinerary
      shortlist. Click <strong>New trip</strong> to start.
    </Message>

    <DataView :value="trips.trips" :layout="layout" v-if="trips.trips.length > 0">
      <template #header>
        <div class="layout-toggle">
          <Button
            :outlined="layout !== 'grid'"
            icon="pi pi-th-large"
            aria-label="grid layout"
            @click="layout = 'grid'"
          />
          <Button
            :outlined="layout !== 'list'"
            icon="pi pi-bars"
            aria-label="list layout"
            @click="layout = 'list'"
          />
        </div>
      </template>
      <template #grid="slot">
        <div class="trip-grid">
          <Card
            v-for="t in slot.items"
            :key="t.id"
            class="trip-card"
            @click="router.push(`/trips/${t.id}`)"
            role="button"
            tabindex="0"
            @keydown.enter="router.push(`/trips/${t.id}`)"
          >
            <template #title>{{ t.name }}</template>
            <template #subtitle>
              <small>created {{ new Date(t.created_at).toLocaleDateString() }}</small>
            </template>
            <template #content>
              <p v-if="t.notes" class="trip-notes-preview">{{ t.notes.slice(0, 120) }}</p>
              <p v-else class="trip-notes-preview empty">No notes yet</p>
            </template>
          </Card>
        </div>
      </template>
      <template #list="slot">
        <div class="trip-list">
          <Card
            v-for="t in slot.items"
            :key="t.id"
            @click="router.push(`/trips/${t.id}`)"
            role="button"
            tabindex="0"
            @keydown.enter="router.push(`/trips/${t.id}`)"
            class="trip-list-card"
          >
            <template #title>{{ t.name }}</template>
            <template #content>
              <small>updated {{ new Date(t.updated_at).toLocaleDateString() }}</small>
            </template>
          </Card>
        </div>
      </template>
    </DataView>

    <Dialog v-model:visible="showCreate" header="New trip" modal :style="{ width: '24rem' }">
      <div class="form-row">
        <label>Trip name</label>
        <InputText v-model="newName" placeholder="e.g. Venice 2026" />
      </div>
      <template #footer>
        <Button label="Cancel" text @click="showCreate = false" />
        <Button label="Create" severity="primary" :disabled="!newName.trim()" @click="createAndOpen" />
      </template>
    </Dialog>
  </section>
</template>

<style scoped>
.dashboard-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem;
}
.dashboard-header h1 { margin: 0; }
.layout-toggle { display: flex; gap: 0.5rem; }
.trip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  padding: 0.5rem 0;
}
.trip-card { cursor: pointer; }
.trip-card:hover, .trip-card:focus { outline: 2px solid var(--p-primary-color); }
.trip-notes-preview { color: var(--color-muted); margin: 0.25rem 0; }
.trip-notes-preview.empty { font-style: italic; }
.trip-list { display: grid; gap: 0.5rem; padding: 0.5rem 0; }
.trip-list-card { cursor: pointer; }
.form-row { display: grid; gap: 0.5rem; margin: 0.5rem 0; }
</style>
