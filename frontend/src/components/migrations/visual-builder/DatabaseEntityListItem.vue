<template>
  <article class="entity-item" draggable="true" :aria-label="`Entity ${entity.name}`" @dragstart="handleDragStart">
    <div class="entity-item-top">
      <span class="drag-handle" aria-hidden="true">::</span>
      <strong>{{ entity.name }}</strong>
      <span class="kind-pill">{{ entity.kind }}</span>
    </div>

    <p class="entity-item-meta">{{ entity.recordsLabel }} <span aria-hidden="true">|</span> {{ entity.fieldsCount }} fields</p>

    <div class="tag-row">
      <span v-for="tag in entity.metadata" :key="`${entity.id}-${tag}`">{{ tag }}</span>
    </div>

    <div class="item-footer">
      <button type="button" class="mini-add-btn" @click="$emit('add-to-canvas', entity.id)">+ Canvas</button>
    </div>

  </article>
</template>

<script setup lang="ts">
import type { DatabaseEntity } from '@/mocks/visualMigrationBuilder.mock'

const props = defineProps<{ entity: DatabaseEntity }>()

defineEmits<{
  (e: 'add-to-canvas', entityId: string): void
}>()

const handleDragStart = (event: DragEvent) => {
  if (!event.dataTransfer) {
    return
  }

  const payload = JSON.stringify({
    entityId: props.entity.id,
  })

  // Keep a custom MIME and a text/plain fallback for better browser compatibility.
  event.dataTransfer.setData('application/x-yggdrasil-entity', payload)
  event.dataTransfer.setData('text/plain', payload)
  event.dataTransfer.effectAllowed = 'copy'
}
</script>

<style scoped>
.entity-item {
  display: grid;
  gap: 8px;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #334155;
  background: linear-gradient(160deg, #111827 0%, #162136 100%);
  cursor: grab;
}

.entity-item:active {
  cursor: grabbing;
}

.entity-item-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.entity-item-top strong {
  font-size: 14px;
  color: #f8fafc;
}

.drag-handle {
  color: #64748b;
  font-weight: 700;
  letter-spacing: 1px;
}

.kind-pill {
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 1px 6px;
  font-size: 10px;
  color: #9fb5cd;
  text-transform: uppercase;
}

.mini-add-btn {
  border: 1px solid rgba(34, 197, 94, 0.35);
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.08);
  color: #a7f3d0;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
}

.item-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 2px;
}

.entity-item-meta {
  margin: 0;
  color: #9eb2c9;
  font-size: 12px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-row span {
  border: 1px solid rgba(51, 65, 85, 0.95);
  border-radius: 5px;
  padding: 1px 6px;
  font-size: 10px;
  color: #8fb0cd;
  background: rgba(15, 23, 42, 0.6);
}

</style>
