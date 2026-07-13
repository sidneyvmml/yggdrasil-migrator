<template>
  <div class="overlay" role="dialog" aria-modal="true" aria-labelledby="clear-canvas-title">
    <div class="modal-card">
      <h3 id="clear-canvas-title">Clear Canvas?</h3>
      <p>This will remove all nodes, connections and unsaved mappings from the current canvas.</p>

      <footer>
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="button" class="btn-danger" @click="$emit('clear-canvas')">Clear Canvas</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'cancel'): void
  (e: 'clear-canvas'): void
}>()
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(2, 6, 23, 0.72);
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal-card {
  width: min(520px, 100%);
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  padding: 16px;
  display: grid;
  gap: 12px;
}

h3,
p {
  margin: 0;
}

h3 {
  color: #f8fafc;
}

p {
  color: #d3e2f4;
  font-size: 13px;
}

footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-secondary,
.btn-danger {
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid #334155;
  background: #0f172a;
  color: #d4e5f7;
}

.btn-danger {
  border: 1px solid rgba(239, 68, 68, 0.5);
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
  color: #ffe6e6;
}
</style>
