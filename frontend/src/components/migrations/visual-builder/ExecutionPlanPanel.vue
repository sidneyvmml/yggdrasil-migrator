<template>
  <aside
    ref="panelRef"
    class="execution-plan"
    :style="panelStyle"
  >
    <h4
      class="drag-handle"
      @pointerdown="startDrag"
    >
      Execution Plan
    </h4>

    <ol>
      <li v-for="step in plan.steps" :key="step">{{ step }}</li>
    </ol>

    <div class="meta-row">
      <small>Strategy</small>
      <strong>{{ plan.strategy }}</strong>
    </div>

    <div class="meta-row">
      <small>Estimated records</small>
      <strong>{{ plan.estimatedRecords }}</strong>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

defineProps<{
  plan: {
    steps: string[]
    strategy: string
    estimatedRecords: string
  }
}>()

const panelRef = ref<HTMLElement | null>(null)
const panelX = ref(886)
const panelY = ref(208)
const DRAG_PADDING = 8

const panelStyle = computed(() => ({
  left: `${panelX.value}px`,
  top: `${panelY.value}px`,
}))

const getDragBounds = () => {
  const panel = panelRef.value
  const parent = panel?.parentElement
  if (!panel || !parent) {
    return null
  }

  const maxX = Math.max(DRAG_PADDING, parent.clientWidth - panel.offsetWidth - DRAG_PADDING)
  const maxY = Math.max(DRAG_PADDING, parent.clientHeight - panel.offsetHeight - DRAG_PADDING)
  return {
    minX: DRAG_PADDING,
    minY: DRAG_PADDING,
    maxX,
    maxY,
  }
}

const clampPosition = (x: number, y: number) => {
  const bounds = getDragBounds()
  if (!bounds) {
    return { x, y }
  }

  return {
    x: Math.min(bounds.maxX, Math.max(bounds.minX, x)),
    y: Math.min(bounds.maxY, Math.max(bounds.minY, y)),
  }
}

const startDrag = (event: PointerEvent) => {
  const panel = panelRef.value
  if (!panel) {
    return
  }

  event.preventDefault()
  const startPointerX = event.clientX
  const startPointerY = event.clientY
  const startX = panelX.value
  const startY = panelY.value

  panel.setPointerCapture(event.pointerId)

  const onMove = (moveEvent: PointerEvent) => {
    const next = clampPosition(
      startX + (moveEvent.clientX - startPointerX),
      startY + (moveEvent.clientY - startPointerY),
    )
    panelX.value = next.x
    panelY.value = next.y
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
.execution-plan {
  position: absolute;
  z-index: 7;
  width: 180px;
  border: 1px solid #334155;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.95);
  padding: 10px;
  display: grid;
  gap: 8px;
}

h4 {
  margin: 0;
  color: #f8fafc;
  font-size: 13px;
}

.drag-handle {
  cursor: grab;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

ol {
  margin: 0;
  padding-left: 16px;
  color: #d8e6f5;
  font-size: 12px;
  display: grid;
  gap: 5px;
}

.meta-row {
  display: grid;
  gap: 2px;
}

small {
  color: #94a3b8;
  font-size: 11px;
}

strong {
  color: #d5e6f8;
  font-size: 12px;
}

@media (max-width: 1380px) {
  .execution-plan {
    position: static;
    width: 100%;
  }

  .drag-handle {
    cursor: default;
  }
}
</style>
