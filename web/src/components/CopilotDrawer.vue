<script setup lang="ts">
import { ref } from "vue";
import Drawer from "primevue/drawer";
import Textarea from "primevue/textarea";
import Button from "primevue/button";
import Card from "primevue/card";
import Tag from "primevue/tag";
import Message from "primevue/message";
import { useCopilotStore } from "@/stores/copilot";

const copilot = useCopilotStore();
const nl = ref("");

async function suggest() {
  if (!nl.value.trim()) return;
  try { await copilot.suggestPreferences(nl.value); }
  catch { /* error surfaces in copilot.lastError */ }
}

function accept(id: number) {
  copilot.markAccepted(id);
  // The page that opened the Drawer is responsible for actually writing the
  // suggested value into the form field — the Drawer just records the
  // acceptance. The wizard subscribes to suggestion changes and applies them.
}
</script>

<template>
  <Drawer
    v-model:visible="copilot.drawerOpen"
    header="LLM copilot"
    position="right"
    :style="{ width: '420px' }"
  >
    <p class="copilot-blurb">
      Describe your trip in plain language. I'll suggest preference values
      you can accept, edit, or reject. I never write to your cost fields
      without labeling them as unverified estimates.
    </p>
    <Textarea
      v-model="nl"
      rows="4"
      placeholder="e.g. family with two toddlers, hate red-eyes, open to a stopover in Madrid"
      class="w-full"
      :autoResize="true"
      aria-label="Describe your trip"
    />
    <div class="copilot-actions">
      <Button
        label="Suggest preferences"
        icon="pi pi-sparkles"
        :loading="copilot.loading"
        :disabled="!nl.trim()"
        @click="suggest"
      />
    </div>
    <Message v-if="copilot.lastError" severity="error">
      {{ copilot.lastError }}
    </Message>

    <div class="suggestion-list">
      <Card
        v-for="s in copilot.suggestions.filter((s) => !s.dismissed)"
        :key="s.id"
        class="suggestion-card"
      >
        <template #title>
          <code>{{ s.path }}</code>
        </template>
        <template #subtitle>
          <Tag v-if="s.unverified" severity="warn">unverified estimate</Tag>
          <span class="conf">{{ Math.round(s.confidence * 100) }}% confidence</span>
        </template>
        <template #content>
          <p class="suggestion-value"><strong>Value:</strong> <code>{{ JSON.stringify(s.value) }}</code></p>
          <p class="suggestion-rationale">{{ s.rationale }}</p>
        </template>
        <template #footer>
          <div class="suggestion-footer">
            <Button v-if="!s.accepted" label="Accept" icon="pi pi-check" size="small" severity="success" @click="accept(s.id)" />
            <Tag v-else severity="success">Accepted</Tag>
            <Button label="Edit" icon="pi pi-pencil" size="small" severity="secondary" text />
            <Button label="Reject" icon="pi pi-times" size="small" severity="secondary" text @click="copilot.dismiss(s.id)" />
          </div>
        </template>
      </Card>
    </div>
  </Drawer>
</template>

<style scoped>
.copilot-blurb { color: var(--color-muted); margin-top: 0; }
.w-full { width: 100%; }
.copilot-actions { margin: 0.5rem 0 1rem; }
.suggestion-list { margin-top: 1rem; display: grid; gap: 0.5rem; }
.suggestion-card { background: var(--color-surface); }
.conf { color: var(--color-muted); font-size: 0.85em; margin-left: 0.5rem; }
.suggestion-value { margin: 0.25rem 0; }
.suggestion-rationale { color: var(--color-muted); font-size: 0.9em; margin: 0.25rem 0; }
.suggestion-footer { display: flex; gap: 0.5rem; align-items: center; }
</style>
