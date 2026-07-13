<template>
  <div class="field-table-wrap">
    <table class="field-table">
      <thead>
        <tr>
          <th>Source Field</th>
          <th>Target Field</th>
          <th>Transform</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.sourceField }}</td>
          <td>{{ row.targetField }}</td>
          <td>{{ row.transform }}</td>
          <td><StatusBadge :status="row.status" :label="statusLabel(row.status)" /></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { FieldMapping, MappingFieldStatus } from '@/mocks/visualMigrationBuilder.mock'
import StatusBadge from './StatusBadge.vue'

defineProps<{ rows: FieldMapping[] }>()

const statusLabel = (status: MappingFieldStatus) => {
  if (status === 'valid') return 'Valid'
  if (status === 'warning') return 'Warning'
  if (status === 'ignored') return 'Ignored'
  return 'Error'
}
</script>

<style scoped>
.field-table-wrap {
  overflow: auto;
  border: 1px solid #334155;
  border-radius: 10px;
}

.field-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 540px;
}

.field-table th,
.field-table td {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid rgba(51, 65, 85, 0.7);
  font-size: 12px;
}

.field-table th {
  color: #94a3b8;
  font-weight: 600;
  background: rgba(15, 23, 42, 0.9);
  position: sticky;
  top: 0;
}

.field-table td {
  color: #e2e8f0;
}

.field-table tr:last-child td {
  border-bottom: none;
}
</style>
