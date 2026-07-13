<template>
  <div class="overlay" role="dialog" aria-modal="true" aria-labelledby="create-table-title">
    <div class="modal-card">
      <h3 id="create-table-title">Create Target Table</h3>

      <label>
        Table name
        <input :value="form.tableName" type="text" @input="$emit('update:field', 'tableName', ($event.target as HTMLInputElement).value)" />
      </label>

      <label>
        Schema
        <input :value="form.schema" type="text" @input="$emit('update:field', 'schema', ($event.target as HTMLInputElement).value)" />
      </label>

      <label>
        Creation mode
        <select :value="form.creationMode" @change="$emit('update:field', 'creationMode', ($event.target as HTMLSelectElement).value)">
          <option>Empty table</option>
          <option>Based on source entity</option>
          <option>Based on mapping output</option>
        </select>
      </label>

      <label>
        Source entity
        <select :value="form.sourceEntity" @change="$emit('update:field', 'sourceEntity', ($event.target as HTMLSelectElement).value)">
          <option>accounts</option>
          <option>orders</option>
          <option>users</option>
          <option>invoices</option>
          <option>products</option>
        </select>
      </label>

      <label>
        Primary key
        <input :value="form.primaryKey" type="text" @input="$emit('update:field', 'primaryKey', ($event.target as HTMLInputElement).value)" />
      </label>

      <footer>
        <button type="button" class="btn-secondary" @click="$emit('cancel')">Cancel</button>
        <button type="button" class="btn-primary" @click="$emit('create-table')">Create Table</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
export type CreateTableForm = {
  tableName: string
  schema: string
  creationMode: string
  sourceEntity: string
  primaryKey: string
}

defineProps<{
  form: CreateTableForm
}>()

defineEmits<{
  (e: 'update:field', field: keyof CreateTableForm, value: string): void
  (e: 'cancel'): void
  (e: 'create-table'): void
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
  width: min(600px, 100%);
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  padding: 16px;
  display: grid;
  gap: 10px;
}

h3 {
  margin: 0;
  color: #f8fafc;
}

label {
  display: grid;
  gap: 6px;
  color: #c4d6ea;
  font-size: 13px;
}

input,
select {
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #d7e8f9;
  padding: 8px 10px;
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
  color: #d4e6f8;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #04210f;
}
</style>
