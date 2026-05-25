import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api/client";
import type { Trip } from "@/api/types";

export const useTripsStore = defineStore("trips", () => {
  const trips = ref<Trip[]>([]);
  const loading = ref(false);

  async function fetchAll() {
    loading.value = true;
    try {
      trips.value = await api.listTrips();
    } finally {
      loading.value = false;
    }
  }

  async function create(body: { name: string; notes?: string }) {
    const t = await api.createTrip(body);
    trips.value.unshift(t);
    return t;
  }

  async function patch(id: number, patch: { name?: string; notes?: string }) {
    const updated = await api.patchTrip(id, patch);
    const idx = trips.value.findIndex((t) => t.id === id);
    if (idx >= 0) trips.value[idx] = updated;
    return updated;
  }

  async function remove(id: number) {
    await api.deleteTrip(id);
    trips.value = trips.value.filter((t) => t.id !== id);
  }

  return { trips, loading, fetchAll, create, patch, remove };
});
