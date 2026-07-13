<template>
  <div class="overlay" role="dialog" aria-modal="true" aria-labelledby="create-mapping-title">
    <div class="modal-card">
      <h3 id="create-mapping-title">Create Migration Mapping?</h3>
      <p>{{ sourceLabel }} will be migrated to {{ targetLabel }}.</p>

      <section>
        <p><strong>Auto mapping found:</strong> 8 of 14 fields</p>
        <h4>Warnings</h4>
        <ul>
          <li>3 fields need transformation</li>
          <li>1 DBRef needs configuration</li>
        </ul>
      </section>

      <footer>
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="button" class="btn-primary" @click="$emit('configure-mapping')">Configure Mapping</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  sourceLabel: string
  targetLabel: string
}>()

defineEmits<{
  (e: 'cancel'): void
  (e: 'configure-mapping'): void
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
  width: min(560px, 100%);
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  padding: 16px;
  display: grid;
  gap: 10px;
}

h3,
h4,
p {
  margin: 0;
}

h3,
h4 {
  color: #f8fafc;
}

p,
li {
  color: #d5e4f5;
  font-size: 13px;
}

ul {
  margin: 0;
  padding-left: 18px;
}

footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-secondary,
.btn-primary {
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid #334155;
  background: #0f172a;
  color: #d5e5f7;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #05220f;
}
</style>
