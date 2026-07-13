<template>
  <section class="status-bar" aria-label="Connection Status">
    <article class="status-card">
      <small>Source</small>
      <strong>{{ sourceEngine }}</strong>
      <span>{{ sourceDatabase }}</span>
      <StatusBadge status="valid" label="Connected - 24ms" />
    </article>

    <div class="connector" aria-hidden="true"></div>

    <article class="status-card">
      <small>Target</small>
      <strong>{{ targetEngine }}</strong>
      <span>{{ targetDatabase }}</span>
      <StatusBadge status="valid" label="Connected - 38ms" />
    </article>
  </section>
</template>

<script setup lang="ts">
import StatusBadge from './StatusBadge.vue'

withDefaults(defineProps<{
  sourceEngine?: string
  targetEngine?: string
  sourceDatabase?: string
  targetDatabase?: string
}>(), {
  sourceEngine: 'MongoDB',
  targetEngine: 'PostgreSQL',
  sourceDatabase: 'source_db',
  targetDatabase: 'target_db',
})
</script>

<style scoped>
.status-bar {
  display: grid;
  grid-template-columns: 1fr 120px 1fr;
  align-items: center;
  gap: 8px;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 10px 12px;
  background: rgba(11, 18, 32, 0.75);
}

.status-card {
  display: grid;
  gap: 4px;
}

.status-card small {
  font-size: 11px;
  color: #94a3b8;
}

.status-card strong {
  font-size: 15px;
  color: #f8fafc;
}

.status-card span {
  font-size: 12px;
  color: #9eb3cb;
}

.connector {
  height: 2px;
  border-top: 2px dashed rgba(34, 197, 94, 0.6);
}

@media (max-width: 900px) {
  .status-bar {
    grid-template-columns: 1fr;
  }

  .connector {
    height: 8px;
    border-top: 0;
    border-left: 2px dashed rgba(34, 197, 94, 0.6);
    width: 2px;
    justify-self: center;
  }
}
</style>
