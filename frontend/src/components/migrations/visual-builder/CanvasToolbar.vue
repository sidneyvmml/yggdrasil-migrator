<template>
  <header class="canvas-toolbar">
    <div class="tool-group">
      <button type="button" :class="['tool', { active: activeMode === 'select' }]" @click="$emit('select-mode')">Select</button>
      <button type="button" :class="['tool', { active: activeMode === 'connect' }]" @click="$emit('connect-mode')">Connect</button>
      <button type="button" class="tool" @click="$emit('auto-layout')">Auto Layout</button>
      <button type="button" class="tool" @click="$emit('validate-flow')">Validate</button>
      <button type="button" class="tool" @click="$emit('clear-canvas')">Clear</button>
    </div>

    <div class="tool-group">
      <button type="button" class="tool" @click="$emit('reset-zoom')">{{ zoomPercent }}%</button>
      <button type="button" class="tool" @click="$emit('zoom-out')">-</button>
      <button type="button" class="tool" @click="$emit('zoom-in')">+</button>
      <button type="button" class="tool" @click="$emit('fit-view')">Fit View</button>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  activeMode: 'select' | 'connect'
  zoomPercent: number
}>()

defineEmits<{
  (e: 'select-mode'): void
  (e: 'connect-mode'): void
  (e: 'auto-layout'): void
  (e: 'validate-flow'): void
  (e: 'clear-canvas'): void
  (e: 'zoom-in'): void
  (e: 'zoom-out'): void
  (e: 'reset-zoom'): void
  (e: 'fit-view'): void
}>()
</script>

<style scoped>
.canvas-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tool-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tool {
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #dce9f7;
  font-size: 12px;
  font-weight: 600;
  padding: 7px 10px;
}

.tool.active {
  border-color: rgba(34, 197, 94, 0.55);
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}
</style>
