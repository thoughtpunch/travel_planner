<script setup lang="ts">
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import InputSwitch from "primevue/inputswitch";
import Select from "primevue/select";
import Card from "primevue/card";
import { useSettingsStore } from "@/stores/settings";

const settings = useSettingsStore();
const currencies = ["USD", "EUR", "GBP", "CAD"];
</script>

<template>
  <h1>Settings</h1>
  <TabView value="general">
    <TabPanel value="general" header="General">
      <Card>
        <template #content>
          <div class="row">
            <label>Dark mode</label>
            <InputSwitch v-model="settings.darkMode" aria-label="Dark mode" />
          </div>
          <div class="row">
            <label>Display currency</label>
            <Select v-model="settings.currency" :options="currencies" />
          </div>
        </template>
      </Card>
    </TabPanel>
    <TabPanel value="llm" header="LLM provider">
      <Card>
        <template #content>
          <div class="row">
            <label>Copilot enabled</label>
            <InputSwitch v-model="settings.copilotEnabled" aria-label="Copilot enabled" />
          </div>
          <p class="muted">
            When disabled, the copilot Drawer toggle disappears from the menubar
            and no <code>/api/copilot/*</code> calls are made from the SPA.
          </p>
        </template>
      </Card>
    </TabPanel>
    <TabPanel value="about" header="About">
      <Card>
        <template #content>
          <p>Trip Planner — LLM-orchestrated trip planning workspace.</p>
          <p class="muted">Phase 2 SPA · PrimeVue 4 · Aura theme.</p>
        </template>
      </Card>
    </TabPanel>
  </TabView>
</template>

<style scoped>
.row { display: flex; gap: 1rem; align-items: center; margin: 0.5rem 0; }
.row label { min-width: 160px; }
.muted { color: var(--color-muted); }
</style>
