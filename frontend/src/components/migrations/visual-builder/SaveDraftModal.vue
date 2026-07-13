<template>
  <div class="overlay" role="dialog" aria-modal="true" aria-labelledby="save-draft-title">
    <div class="modal-card">
      <h3 id="save-draft-title">Save Migration Draft</h3>

      <label>
        Draft name
        <input :value="draftName" type="text" @input="$emit('update:draftName', ($event.target as HTMLInputElement).value)" />
      </label>

      <label>
        Description
        <textarea :value="description" rows="4" @input="$emit('update:description', ($event.target as HTMLTextAreaElement).value)"></textarea>
      </label>

      <footer>
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="button" class="btn-primary" @click="$emit('save')">Save Draft</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  draftName: string
  description: string
}>()

defineEmits<{
  (e: 'update:draftName', value: string): void
  (e: 'update:description', value: string): void
  (e: 'cancel'): void
  (e: 'save'): void
}>()
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(2, 6, 23, 0.7);
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
  gap: 12px;
}

h3 {
  margin: 0;
  color: #f8fafc;
}

label {
  display: grid;
  gap: 6px;
  color: #c6d7ea;
  font-size: 13px;
}

input,
textarea {
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #d9e9fa;
  padding: 9px 10px;
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
  color: #d4e5f7;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.5);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #04220f;
}
</style>
