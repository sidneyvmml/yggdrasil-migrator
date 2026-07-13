<template>
  <span :class="['vb-status-badge', toneClass]">
    <span class="vb-status-dot" aria-hidden="true"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: 'valid' | 'warning' | 'ignored' | 'error' | 'ready' | 'needs_review' | 'not_connected' | 'neutral'
  label: string
}>()

const toneClass = computed(() => {
  const map = {
    valid: 'is-valid',
    ready: 'is-valid',
    warning: 'is-warning',
    needs_review: 'is-warning',
    ignored: 'is-neutral',
    not_connected: 'is-neutral',
    neutral: 'is-neutral',
    error: 'is-error',
  }
  return map[props.status]
})
</script>

<style scoped>
.vb-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}

.vb-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.9;
}

.is-valid {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.4);
}

.is-warning {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.4);
}

.is-neutral {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.1);
  border-color: rgba(148, 163, 184, 0.35);
}

.is-error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.4);
}
</style>
