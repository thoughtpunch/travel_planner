<script setup lang="ts">
import Badge from "primevue/badge";

const props = defineProps<{ delta: number; reason?: string }>();
</script>

<template>
  <span
    v-if="props.delta !== 0"
    v-tooltip.top="props.reason"
    class="rank-delta"
    :aria-label="`rank ${props.delta > 0 ? 'up' : 'down'} ${Math.abs(props.delta)}`"
  >
    <Badge
      :value="`${props.delta > 0 ? '+' : ''}${props.delta}`"
      :severity="props.delta > 0 ? 'success' : 'danger'"
    />
  </span>
  <span v-else aria-label="no rank change" class="rank-delta-zero">—</span>
</template>

<style scoped>
.rank-delta-zero { color: var(--color-muted); }
</style>
