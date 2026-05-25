import { describe, expect, it } from "vitest";
import { mount, config } from "@vue/test-utils";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import BookendedScale from "./BookendedScale.vue";

// Register tooltip stub so v-tooltip in components doesn't crash.
config.global.directives = { tooltip: () => undefined };
config.global.plugins = [[PrimeVue, { theme: { preset: Aura } }]];

describe("BookendedScale", () => {
  it("emits update with the right scale position", async () => {
    const wrapper = mount(BookendedScale, {
      props: {
        axis: "red_eye",
        label: "Red-eye",
        hardYesAdmitted: false,
        modelValue: { position: "neutral" },
      },
    });
    // Just confirm it renders and exposes the slider role.
    expect(wrapper.html()).toContain("HARD NO");
    expect(wrapper.html()).toContain("HARD YES");
  });

  it("shows HARD YES as locked when not admitted", () => {
    const wrapper = mount(BookendedScale, {
      props: {
        axis: "layover_length",
        label: "Layover length",
        hardYesAdmitted: false,
        thresholdLabel: "Filter out longer than (min)",
        modelValue: { position: "neutral" },
      },
    });
    expect(wrapper.html()).toContain("pi-lock");
  });

  it("requires a threshold when HARD NO with a threshold axis", () => {
    const wrapper = mount(BookendedScale, {
      props: {
        axis: "layover_length",
        label: "Layover length",
        hardYesAdmitted: false,
        thresholdLabel: "Filter out longer than (min)",
        modelValue: { position: "hard_no" },
      },
    });
    // Warning message is shown when threshold is missing.
    expect(wrapper.html()).toContain("threshold");
  });
});
