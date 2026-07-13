<template>
  <div class="edge-layer" :style="layerStyle">
    <svg class="edge-svg" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none" aria-hidden="true">
      <path :d="pathD" :class="['edge-path', connection.status === 'needs_review' ? 'warn' : 'ok']" />
    </svg>

    <div class="edge-label" :style="labelStyle">
      <strong>{{ connection.label }}</strong>
      <p v-if="typeof connection.mappedFields === 'number' && typeof connection.totalFields === 'number'">
        Mapping {{ connection.mappedFields }}/{{ connection.totalFields }} fields
      </p>
      <StatusBadge
        :status="connection.status === 'needs_review' ? 'needs_review' : connection.status === 'error' ? 'error' : 'ready'"
        :label="connection.subtitle || (connection.status === 'needs_review' ? 'Needs review' : 'Mapping ready')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CanvasConnection } from '@/mocks/visualMigrationBuilder.mock'
import StatusBadge from './StatusBadge.vue'

const props = defineProps<{
  connection: CanvasConnection
  startX: number
  startY: number
  endX: number
  endY: number
}>()

const width = computed(() => Math.abs(props.endX - props.startX) + 12)
const height = computed(() => Math.abs(props.endY - props.startY) + 12)

const fromLeft = computed(() => Math.min(props.startX, props.endX))
const fromTop = computed(() => Math.min(props.startY, props.endY))

const pathD = computed(() => {
  const sx = props.startX <= props.endX ? 6 : width.value - 6
  const ex = props.startX <= props.endX ? width.value - 6 : 6
  const sy = props.startY <= props.endY ? 6 : height.value - 6
  const ey = props.startY <= props.endY ? height.value - 6 : 6
  const cx = width.value / 2
  return `M ${sx} ${sy} C ${cx} ${sy}, ${cx} ${ey}, ${ex} ${ey}`
})

const layerStyle = computed(() => ({
  left: `${fromLeft.value}px`,
  top: `${fromTop.value}px`,
  width: `${width.value}px`,
  height: `${height.value}px`,
}))

const labelStyle = computed(() => ({
  left: `${fromLeft.value + width.value / 2 - 70}px`,
  top: `${fromTop.value + height.value / 2 - 26}px`,
}))
</script>

<style scoped>
.edge-layer {
  position: absolute;
}

.edge-svg {
  position: absolute;
}

.edge-path {
  fill: none;
  stroke-width: 2.2;
  stroke-linecap: round;
}

.edge-path.ok {
  stroke: #22c55e;
}

.edge-path.warn {
  stroke: #f59e0b;
}

.edge-label {
  position: absolute;
  width: 140px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.96);
  padding: 7px;
  display: grid;
  gap: 4px;
}

.edge-label strong {
  color: #e2e8f0;
  font-size: 11px;
}

.edge-label p {
  margin: 0;
  color: #9eb3cb;
  font-size: 11px;
}
</style>
