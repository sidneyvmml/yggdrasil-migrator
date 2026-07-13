<template>
  <footer class="flow-validation">
    <div class="flow-header">
      <h4>Flow Validation</h4>
      <button type="button" class="details-btn" @click="$emit('open-details')">Details</button>
    </div>

    <div class="stats-grid">
      <article v-for="item in items" :key="item.id" :class="['stat-item', toneClass(item.tone)]">
        <strong>{{ item.label }}</strong>
        <p>{{ item.description }}</p>
      </article>
    </div>
  </footer>
</template>

<script setup lang="ts">
type ValidationTone = 'valid' | 'warning' | 'neutral' | 'error'

defineProps<{
  items: Array<{
    id: string
    label: string
    description: string
    tone: ValidationTone
  }>
}>()

defineEmits<{
  (e: 'open-details'): void
}>()

const toneClass = (tone: ValidationTone): string => {
  if (tone === 'valid') return 'tone-valid'
  if (tone === 'warning') return 'tone-warning'
  if (tone === 'error') return 'tone-error'
  return 'tone-neutral'
}
</script>

<style scoped>
.flow-validation {
  border: 1px solid #334155;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.84);
  padding: 10px;
  display: grid;
  gap: 10px;
}

.flow-validation h4 {
  margin: 0;
  color: #f8fafc;
  font-size: 14px;
}

.flow-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.details-btn {
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #d5e6f8;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 9px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(120px, 1fr));
  gap: 8px;
}

.stat-item {
  border: 1px solid #334155;
  border-radius: 9px;
  padding: 8px;
  display: grid;
  gap: 4px;
}

.stat-item strong {
  font-size: 24px;
  line-height: 1;
}

.stat-item p {
  margin: 0;
  color: #9cb1c9;
  font-size: 11px;
}

.tone-valid strong {
  color: #22c55e;
}

.tone-warning strong {
  color: #f59e0b;
}

.tone-neutral strong {
  color: #94a3b8;
}

.tone-error strong {
  color: #ef4444;
}

@media (max-width: 1380px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(120px, 1fr));
  }
}

@media (max-width: 860px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
