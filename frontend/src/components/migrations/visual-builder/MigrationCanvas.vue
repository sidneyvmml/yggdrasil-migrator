<template>
  <section class="canvas-panel">
    <header class="canvas-header">
      <h3>Migration Canvas</h3>
      <CanvasToolbar
        :active-mode="activeMode"
        :zoom-percent="zoomPercent"
        @select-mode="$emit('select-mode')"
        @connect-mode="$emit('connect-mode')"
        @auto-layout="$emit('auto-layout')"
        @validate-flow="$emit('validate-flow')"
        @clear-canvas="$emit('clear-canvas')"
        @zoom-in="$emit('zoom-in')"
        @zoom-out="$emit('zoom-out')"
        @reset-zoom="$emit('reset-zoom')"
        @fit-view="$emit('fit-view')"
      />
    </header>

    <div
      ref="canvasBodyRef"
      :class="['canvas-body', { 'is-drag-over': isDragOver }]"
      aria-label="Migration flow canvas"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <div
        class="canvas-content"
        :style="canvasTransformStyle"
        @dragover.prevent.stop="handleDragOver"
        @drop.prevent.stop="handleDrop"
      >
        <div v-if="isDragOver && dragPreview" class="drag-preview" :style="dragPreviewStyle">
          <strong>{{ dragPreview.entityName }}</strong>
          <small>Drop to place on canvas</small>
        </div>

        <div v-if="nodes.length === 0" class="empty-state">
          <p>Your canvas is empty.</p>
          <small>Drag source and target entities here to start building a migration flow.</small>
        </div>

        <div
          v-for="connection in connections"
          :key="connection.id"
          class="edge-wrapper"
        >
          <CanvasConnectionEdge
            v-if="edgePoint(connection.sourceNodeId, 'out') && edgePoint(connection.targetNodeId, 'in')"
            :connection="connection"
            :start-x="edgePoint(connection.sourceNodeId, 'out')!.x"
            :start-y="edgePoint(connection.sourceNodeId, 'out')!.y"
            :end-x="edgePoint(connection.targetNodeId, 'in')!.x"
            :end-y="edgePoint(connection.targetNodeId, 'in')!.y"
          />
        </div>

        <CanvasEntityNode
          v-for="node in nodes"
          :key="node.id"
          :node="node"
          :entity="entityById[node.entityId]"
          :is-selected="selectedNodeId === node.id"
          :is-connect-source="connectSourceNodeId === node.id"
          @node-selected="$emit('node-selected', $event)"
          @preview-node="$emit('preview-node', $event)"
          @map-fields="$emit('map-fields', $event)"
          @schema-details="$emit('schema-details', $event)"
          @drag-start="startNodeDrag"
        />

        <ExecutionPlanPanel :plan="plan" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CanvasConnection, CanvasNode, DatabaseEntity } from '@/mocks/visualMigrationBuilder.mock'
import CanvasToolbar from './CanvasToolbar.vue'
import CanvasEntityNode from './CanvasEntityNode.vue'
import CanvasConnectionEdge from './CanvasConnectionEdge.vue'
import ExecutionPlanPanel from './ExecutionPlanPanel.vue'

const props = defineProps<{
  activeMode: 'select' | 'connect'
  zoomPercent: number
  selectedNodeId?: string | null
  connectSourceNodeId?: string | null
  nodes: CanvasNode[]
  entities: DatabaseEntity[]
  connections: CanvasConnection[]
  plan: {
    steps: string[]
    strategy: string
    estimatedRecords: string
  }
}>()

const emit = defineEmits<{
  (e: 'select-mode'): void
  (e: 'connect-mode'): void
  (e: 'auto-layout'): void
  (e: 'validate-flow'): void
  (e: 'clear-canvas'): void
  (e: 'zoom-in'): void
  (e: 'zoom-out'): void
  (e: 'reset-zoom'): void
  (e: 'fit-view'): void
  (e: 'node-selected', node: CanvasNode): void
  (e: 'preview-node', entity: DatabaseEntity): void
  (e: 'map-fields', entity: DatabaseEntity): void
  (e: 'schema-details', entity: DatabaseEntity): void
  (e: 'drop-entity', payload: { entityId: string; x: number; y: number }): void
  (e: 'move-node', payload: { nodeId: string; x: number; y: number }): void
}>()

const canvasBodyRef = ref<HTMLElement | null>(null)
const isDragOver = ref(false)
const dragPreview = ref<{ entityId: string; entityName: string; x: number; y: number } | null>(null)
const CANVAS_WIDTH = 1080
const CANVAS_HEIGHT = 760
const NODE_WIDTH = 238
const NODE_HEIGHT = 220
const EDGE_PADDING = 20

const clampToCanvas = (x: number, y: number): { x: number; y: number } => {
  const clampedX = Math.min(
    CANVAS_WIDTH - NODE_WIDTH - EDGE_PADDING,
    Math.max(EDGE_PADDING, Math.round(x)),
  )
  const clampedY = Math.min(
    CANVAS_HEIGHT - NODE_HEIGHT - EDGE_PADDING,
    Math.max(EDGE_PADDING, Math.round(y)),
  )
  return {
    x: clampedX,
    y: clampedY,
  }
}

const canvasTransformStyle = computed(() => ({
  transform: `scale(${props.zoomPercent / 100})`,
}))

const dragPreviewStyle = computed(() => {
  if (!dragPreview.value) {
    return {}
  }

  return {
    left: `${dragPreview.value.x}px`,
    top: `${dragPreview.value.y}px`,
  }
})

const entityById = computed<Record<string, DatabaseEntity>>(() => {
  return props.entities.reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {} as Record<string, DatabaseEntity>)
})

const nodeById = computed<Record<string, CanvasNode>>(() => {
  return props.nodes.reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {} as Record<string, CanvasNode>)
})

const edgePoint = (nodeId: string, side: 'in' | 'out'): { x: number; y: number } | null => {
  const node = nodeById.value[nodeId]
  if (!node) return null

  const x = side === 'out' ? node.x + 236 : node.x
  const y = node.y + 108
  return { x, y }
}

const getEntityIdFromDragEvent = (event: DragEvent): string | null => {
  const dataTransfer = event.dataTransfer
  if (!dataTransfer) {
    return null
  }

  const candidates = [
    dataTransfer.getData('application/x-yggdrasil-entity'),
    dataTransfer.getData('text/plain'),
  ]

  for (const raw of candidates) {
    if (!raw) {
      continue
    }
    try {
      const parsed = JSON.parse(raw) as { entityId?: string }
      if (parsed.entityId) {
        return parsed.entityId
      }
    } catch {
      continue
    }
  }

  return null
}

const handleDragOver = (event: DragEvent) => {
  isDragOver.value = true
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }

  if (!canvasBodyRef.value) {
    return
  }

  const entityId = getEntityIdFromDragEvent(event)
  if (!entityId) {
    return
  }

  const entity = entityById.value[entityId]
  const rect = canvasBodyRef.value.getBoundingClientRect()
  const scale = props.zoomPercent / 100
  const x = ((event.clientX - rect.left + canvasBodyRef.value.scrollLeft) / scale) - 119
  const y = ((event.clientY - rect.top + canvasBodyRef.value.scrollTop) / scale) - 70
  const clamped = clampToCanvas(x, y)

  dragPreview.value = {
    entityId,
    entityName: entity?.name || entityId,
    x: clamped.x,
    y: clamped.y,
  }
}

const handleDragLeave = (event: DragEvent) => {
  const target = event.currentTarget as HTMLElement | null
  const related = event.relatedTarget as Node | null
  if (!target || !related || !target.contains(related)) {
    isDragOver.value = false
    dragPreview.value = null
  }
}

const handleDrop = (event: DragEvent) => {
  const fallbackEntityId = dragPreview.value?.entityId || null
  const fallbackX = dragPreview.value?.x ?? null
  const fallbackY = dragPreview.value?.y ?? null

  isDragOver.value = false
  dragPreview.value = null
  if (!canvasBodyRef.value) {
    return
  }

  const entityId = getEntityIdFromDragEvent(event) || fallbackEntityId
  if (!entityId) {
    return
  }

  try {
    let clamped: { x: number; y: number }

    if (fallbackX !== null && fallbackY !== null) {
      clamped = clampToCanvas(fallbackX, fallbackY)
    } else {
      const rect = canvasBodyRef.value.getBoundingClientRect()
      const scale = props.zoomPercent / 100
      const x = ((event.clientX - rect.left + canvasBodyRef.value.scrollLeft) / scale) - 119
      const y = ((event.clientY - rect.top + canvasBodyRef.value.scrollTop) / scale) - 70
      const grid = 20
      const snappedX = Math.round(x / grid) * grid
      const snappedY = Math.round(y / grid) * grid
      clamped = clampToCanvas(snappedX, snappedY)
    }

    emit('drop-entity', {
      entityId,
      x: clamped.x,
      y: clamped.y,
    })
  } catch {
    // Ignore invalid drag payload.
  }
}

const startNodeDrag = (payload: { node: CanvasNode; event: PointerEvent }) => {
  if (!canvasBodyRef.value) {
    return
  }

  const startX = payload.node.x
  const startY = payload.node.y
  const pointerStartX = payload.event.clientX
  const pointerStartY = payload.event.clientY
  const scale = props.zoomPercent / 100
  const grid = 20

  const onMove = (event: PointerEvent) => {
    const deltaX = (event.clientX - pointerStartX) / scale
    const deltaY = (event.clientY - pointerStartY) / scale
    const rawX = startX + deltaX
    const rawY = startY + deltaY
    const snappedX = Math.round(rawX / grid) * grid
    const snappedY = Math.round(rawY / grid) * grid
    const clamped = clampToCanvas(snappedX, snappedY)

    emit('move-node', {
      nodeId: payload.node.id,
      x: clamped.x,
      y: clamped.y,
    })
  }

  const onEnd = () => {
    window.removeEventListener('pointermove', onMove)
    window.removeEventListener('pointerup', onEnd)
  }

  window.addEventListener('pointermove', onMove)
  window.addEventListener('pointerup', onEnd, { once: true })
}
</script>

<style scoped>
.canvas-panel {
  border: 1px solid #334155;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.8);
  padding: 12px;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 12px;
  min-height: 0;
}

.canvas-header {
  display: grid;
  gap: 10px;
}

.canvas-header h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 16px;
}

.canvas-body {
  position: relative;
  min-height: 700px;
  overflow: auto;
  border-radius: 10px;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background-color: #0b1220;
  background-image:
    radial-gradient(circle at 1px 1px, rgba(100, 116, 139, 0.35) 1px, transparent 0);
  background-size: 20px 20px;
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.canvas-body.is-drag-over {
  border-color: rgba(6, 182, 212, 0.7);
  box-shadow: inset 0 0 0 2px rgba(6, 182, 212, 0.35);
}

.canvas-content {
  position: relative;
  width: 1080px;
  min-height: 760px;
  transform-origin: top left;
}

.drag-preview {
  position: absolute;
  width: 238px;
  border-radius: 12px;
  border: 1px dashed rgba(6, 182, 212, 0.8);
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
  padding: 10px;
  pointer-events: none;
  z-index: 6;
}

.drag-preview strong {
  display: block;
  color: #e0f2fe;
  font-size: 13px;
  margin-bottom: 4px;
}

.drag-preview small {
  color: #9cc3de;
  font-size: 11px;
}

.edge-wrapper {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.empty-state {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  gap: 8px;
  text-align: center;
  padding: 20px;
}

.empty-state p {
  margin: 0;
  color: #dce9f8;
  font-size: 16px;
  font-weight: 600;
}

.empty-state small {
  color: #9bb0c8;
  font-size: 12px;
}
</style>
