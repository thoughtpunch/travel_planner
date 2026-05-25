<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import Menubar from "primevue/menubar";
import Button from "primevue/button";
import InputSwitch from "primevue/inputswitch";
import Toast from "primevue/toast";
import ConfirmDialog from "primevue/confirmdialog";
import { useSettingsStore } from "@/stores/settings";
import { useCopilotStore } from "@/stores/copilot";
import CopilotDrawer from "@/components/CopilotDrawer.vue";

const settings = useSettingsStore();
const copilot = useCopilotStore();
const router = useRouter();

const menuItems = ref([
  { label: "Dashboard", icon: "pi pi-home", command: () => router.push("/") },
  { label: "Settings", icon: "pi pi-cog", command: () => router.push("/settings") },
]);
</script>

<template>
  <div class="app-shell">
    <Menubar :model="menuItems" class="app-menubar">
      <template #start>
        <strong class="logo">Trip Planner</strong>
      </template>
      <template #end>
        <div class="menu-end">
          <span class="dark-toggle">
            <i class="pi pi-moon" aria-hidden="true"></i>
            <InputSwitch
              v-model="settings.darkMode"
              aria-label="Toggle dark mode"
            />
          </span>
          <Button
            v-if="settings.copilotEnabled"
            icon="pi pi-sparkles"
            severity="secondary"
            text
            rounded
            aria-label="Open copilot"
            @click="copilot.toggleDrawer()"
          />
        </div>
      </template>
    </Menubar>

    <main id="main" class="app-main">
      <router-view />
    </main>

    <CopilotDrawer v-if="settings.copilotEnabled" />
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<style>
.app-shell {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}
.app-menubar {
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
}
.logo {
  margin-right: 1rem;
  font-size: 1.05rem;
}
.menu-end {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.dark-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.app-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}
</style>
