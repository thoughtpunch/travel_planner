<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import { api } from "@/api/client";
import type { Trip } from "@/api/types";
import StatusBadge from "@/components/StatusBadge.vue";

const props = defineProps<{ trip: Trip }>();
const runs = ref<any[]>([]);
const router = useRouter();

onMounted(async () => { runs.value = await api.listRuns(props.trip.id); });
</script>

<template>
  <DataTable :value="runs" stripedRows :rowsPerPageOptions="[10, 20, 50]">
    <Column field="id" header="#" sortable />
    <Column field="status" header="Status" sortable>
      <template #body="{ data }"><StatusBadge :status="data.status" /></template>
    </Column>
    <Column field="started_at" header="Started" sortable>
      <template #body="{ data }">{{ new Date(data.started_at).toLocaleString() }}</template>
    </Column>
    <Column field="scraper_calls" header="Scraper" />
    <Column field="serpapi_calls" header="SerpAPI" />
    <Column header="">
      <template #body="{ data }">
        <Button label="Open" size="small" outlined @click="router.push(`/trips/${trip.id}/runs/${data.id}`)" />
      </template>
    </Column>
  </DataTable>
</template>
