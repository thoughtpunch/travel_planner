import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api/client";
import type { CopilotSuggestion } from "@/api/types";

export interface SuggestionEntry extends CopilotSuggestion {
  id: number;
  dismissed: boolean;
  accepted: boolean;
}

let nextId = 1;

export const useCopilotStore = defineStore("copilot", () => {
  const drawerOpen = ref(false);
  const suggestions = ref<SuggestionEntry[]>([]);
  const loading = ref(false);
  const lastError = ref<string | null>(null);

  async function suggestPreferences(nl: string) {
    loading.value = true;
    lastError.value = null;
    try {
      const resp = await api.suggestPreferences(nl);
      const entries = resp.suggestions.map((s) => ({
        ...s,
        id: nextId++,
        dismissed: false,
        accepted: false,
      }));
      suggestions.value = [...entries, ...suggestions.value];
    } catch (e) {
      lastError.value = (e as Error).message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function suggestCostAssumptions(tripContext: Record<string, unknown>) {
    loading.value = true;
    lastError.value = null;
    try {
      const resp = await api.suggestCostAssumptions(tripContext);
      const entries = resp.suggestions.map((s) => ({
        ...s,
        id: nextId++,
        dismissed: false,
        accepted: false,
      }));
      suggestions.value = [...entries, ...suggestions.value];
    } catch (e) {
      lastError.value = (e as Error).message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function markAccepted(id: number) {
    const s = suggestions.value.find((s) => s.id === id);
    if (s) s.accepted = true;
  }

  function dismiss(id: number) {
    const s = suggestions.value.find((s) => s.id === id);
    if (s) s.dismissed = true;
  }

  function toggleDrawer() {
    drawerOpen.value = !drawerOpen.value;
  }

  return {
    drawerOpen,
    suggestions,
    loading,
    lastError,
    suggestPreferences,
    suggestCostAssumptions,
    markAccepted,
    dismiss,
    toggleDrawer,
  };
});
