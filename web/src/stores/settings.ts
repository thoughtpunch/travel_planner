import { defineStore } from "pinia";
import { ref, watch } from "vue";

const KEY = "trip-planner-settings-v1";

interface SettingsShape {
  darkMode: boolean;
  copilotEnabled: boolean;
  currency: string;
}

function load(): SettingsShape {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { darkMode: false, copilotEnabled: true, currency: "USD", ...JSON.parse(raw) };
  } catch { /* ignore */ }
  return { darkMode: false, copilotEnabled: true, currency: "USD" };
}

export const useSettingsStore = defineStore("settings", () => {
  const initial = load();
  const darkMode = ref(initial.darkMode);
  const copilotEnabled = ref(initial.copilotEnabled);
  const currency = ref(initial.currency);

  function applyDarkMode() {
    document.documentElement.classList.toggle("dark", darkMode.value);
  }
  applyDarkMode();

  watch([darkMode, copilotEnabled, currency], () => {
    localStorage.setItem(
      KEY,
      JSON.stringify({
        darkMode: darkMode.value,
        copilotEnabled: copilotEnabled.value,
        currency: currency.value,
      }),
    );
    applyDarkMode();
  });

  return { darkMode, copilotEnabled, currency };
});
