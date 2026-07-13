<template>
  <article
    :class="['canvas-node', statusClass, { 'is-selected': isSelected, 'is-connect-source': isConnectSource } ]"
    :style="styleObject"
    @click="emit('node-selected', node)"
  >
    <div class="node-badges">
      <small class="engine">{{ engineLabel }}</small>
      <span :class="['role-badge', roleClass]">{{ roleLabel }}</span>
      <button
        type="button"
        class="drag-node-btn"
        title="Arrastar card"
        aria-label="Arrastar card"
        data-tooltip="Segure e arraste"
        @pointerdown.stop.prevent="onDragHandlePointerDown"
      >
        ::
      </button>
    </div>
    <h4>{{ entity.name }}</h4>
    <p class="kind">{{ entity.kind === 'collection' ? 'Collection' : 'Table' }}</p>
    <p class="records">{{ entity.recordsLabel }}</p>
    <p class="fields">{{ entity.fieldsCount }} fields</p>

    <ul>
      <li v-for="line in entity.details" :key="`${entity.id}-${line}`">{{ line }}</li>
    </ul>

    <div class="node-actions">
      <button type="button" @click.stop="$emit('preview-node', entity)">Preview</button>
      <button
        v-if="entity.kind === 'collection'"
        type="button"
        @click.stop="$emit('map-fields', entity)"
      >
        Map Fields
      </button>
      <button
        v-else
        type="button"
        @click.stop="$emit('schema-details', entity)"
      >
        Schema
      </button>
    </div>

    <StatusBadge
      v-if="node.status === 'not_connected'"
      status="not_connected"
      label="Not connected"
    />
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatusBadge from './StatusBadge.vue'
import type { CanvasNode, DatabaseEntity } from '@/mocks/visualMigrationBuilder.mock'

const props = defineProps<{
  entity: DatabaseEntity
  node: CanvasNode
  isSelected?: boolean
  isConnectSource?: boolean
}>()

const emit = defineEmits<{
  (e: 'node-selected', node: CanvasNode): void
  (e: 'preview-node', entity: DatabaseEntity): void
  (e: 'map-fields', entity: DatabaseEntity): void
  (e: 'schema-details', entity: DatabaseEntity): void
  (e: 'drag-start', payload: { node: CanvasNode; event: PointerEvent }): void
}>()

const onDragHandlePointerDown = (event: PointerEvent) => {
  if (event.button !== 0) {
    return
  }
  emit('drag-start', { node: props.node, event })
}

const engineLabel = computed(() => (props.entity.engine === 'mongodb' ? 'MongoDB' : 'PostgreSQL'))

const roleLabel = computed(() => {
  return props.node.entityId.startsWith('src-') ? 'Source' : 'Target'
})

const roleClass = computed(() => {
  return props.node.entityId.startsWith('src-') ? 'role-source' : 'role-target'
})

const styleObject = computed(() => ({
  left: `${props.node.x}px`,
  top: `${props.node.y}px`,
}))

const statusClass = computed(() => {
  if (props.node.status === 'needs_review') return 'status-needs-review'
  if (props.node.status === 'ready') return 'status-ready'
  if (props.node.status === 'not_connected') return 'status-not-connected'
  return 'status-default'
})
</script>

<style scoped>
.canvas-node {
  position: absolute;
  width: 238px;
  border-radius: 12px;
  border: 1px solid #334155;
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(14, 24, 41, 0.95) 100%);
  padding: 12px;
  display: grid;
  gap: 5px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  cursor: pointer;
}

.drag-node-btn {
  position: relative;
  margin-left: auto;
  width: 24px;
  height: 20px;
  border: 1px solid #334155;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.9);
  color: #93a8be;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  cursor: grab;
}

.drag-node-btn:active {
  cursor: grabbing;
}

.drag-node-btn::after {
  content: attr(data-tooltip);
  position: absolute;
  right: 0;
  bottom: calc(100% + 6px);
  white-space: nowrap;
  font-size: 10px;
  font-weight: 600;
  color: #dbe8f8;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 4px 6px;
  opacity: 0;
  transform: translateY(4px);
  pointer-events: none;
  transition: opacity 0.12s ease, transform 0.12s ease;
}

.drag-node-btn:hover::after,
.drag-node-btn:focus-visible::after {
  opacity: 1;
  transform: translateY(0);
}

.engine {
  color: #93c5fd;
  font-size: 10px;
  letter-spacing: 0.2px;
}

.node-badges {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
}

.role-badge {
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2px;
  text-transform: uppercase;
}

.role-source {
  border-color: rgba(34, 197, 94, 0.45);
  color: #86efac;
  background: rgba(34, 197, 94, 0.12);
}

.role-target {
  border-color: rgba(6, 182, 212, 0.45);
  color: #67e8f9;
  background: rgba(6, 182, 212, 0.12);
}

h4 {
  margin: 0;
  color: #f8fafc;
  font-size: 16px;
}

.kind,
.records,
.fields {
  margin: 0;
  color: #9cb1c9;
  font-size: 12px;
}

ul {
  margin: 5px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 2px;
}

li {
  font-size: 12px;
  color: #7fa2c2;
}

.node-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.node-actions button {
  border: 1px solid #334155;
  border-radius: 7px;
  background: #0f172a;
  color: #d7e6f7;
  font-size: 11px;
  padding: 5px 8px;
}

.status-needs-review {
  border-color: rgba(245, 158, 11, 0.45);
}

.status-ready {
  border-color: rgba(34, 197, 94, 0.45);
}

.status-not-connected {
  border-style: dashed;
  border-color: rgba(148, 163, 184, 0.45);
}

.is-selected {
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.55), 0 12px 28px rgba(0, 0, 0, 0.35);
}

.is-connect-source {
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.62), 0 12px 28px rgba(0, 0, 0, 0.35);
}
</style>
