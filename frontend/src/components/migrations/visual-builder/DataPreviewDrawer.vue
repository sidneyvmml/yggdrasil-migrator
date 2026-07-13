<template>
  <aside class="drawer" aria-label="Data Preview">
    <header>
      <h3>Data Preview</h3>
      <button type="button" aria-label="Close preview" @click="$emit('close')">x</button>
    </header>

    <p class="entity-label">{{ entityName }}</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <section v-if="kind === 'mongodb'" class="json-panel">
      <p v-if="loading" class="state-message">Loading preview data...</p>
      <pre v-else>{{ mongoPreviewContent }}</pre>
    </section>

    <section v-else class="table-panel">
      <p v-if="loading" class="state-message">Loading preview data...</p>
      <table v-else>
        <thead>
          <tr>
            <th v-for="column in normalizedColumns" :key="column">{{ column }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in normalizedRows" :key="`row-${rowIndex}`">
            <td v-for="column in normalizedColumns" :key="`${rowIndex}-${column}`">{{ row[column] }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <footer>
      <button type="button" class="btn-secondary" @click="$emit('close')">Close</button>
      <button type="button" class="btn-primary" :disabled="loading" @click="$emit('map-fields')">Map Fields</button>
    </footer>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineEmits<{
  (e: 'close'): void
  (e: 'map-fields'): void
}>()

const fallbackMongoPreview = `{
  "_id": "665f8a3e1c2b4d5e7f8a9b10",
  "name": "Joao Silva",
  "documentId": "12341",
  "email": "joao@email.com",
  "address": {
    "street": "Rua das Flores, 123",
    "city": "Sao Paulo",
    "state": "SP",
    "zipCode": "01000-000"
  },
  "createdAt": "2024-05-20T14:30:00Z",
  "tags": ["premium", "active"]
}`

const props = defineProps<{
  kind: 'mongodb' | 'postgresql'
  entityName: string
  mongoSample?: Record<string, any> | null
  tableColumns?: string[]
  tableRows?: Array<Record<string, any>>
  loading?: boolean
  errorMessage?: string
}>()

const mongoPreviewContent = computed(() => {
  if (props.mongoSample && Object.keys(props.mongoSample).length > 0) {
    return JSON.stringify(props.mongoSample, null, 2)
  }
  return fallbackMongoPreview
})

const fallbackColumns = ['id', 'name_client', 'document', 'email', 'city', 'state']
const fallbackRows = [
  {
    id: 'cl_9201',
    name_client: 'Joao Silva',
    document: '12341',
    email: 'joao@email.com',
    city: 'Sao Paulo',
    state: 'SP',
  },
]

const normalizedColumns = computed(() => {
  if (props.tableColumns && props.tableColumns.length > 0) {
    return props.tableColumns
  }
  return fallbackColumns
})

const normalizedRows = computed(() => {
  if (props.tableRows && props.tableRows.length > 0) {
    return props.tableRows.map((row) => {
      const normalized: Record<string, string> = {}
      normalizedColumns.value.forEach((column) => {
        const value = row[column]
        normalized[column] = value === undefined || value === null
          ? '-'
          : typeof value === 'object'
            ? JSON.stringify(value)
            : String(value)
      })
      return normalized
    })
  }
  return fallbackRows
})
</script>

<style scoped>
.drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 55;
  width: min(520px, 100%);
  border-left: 1px solid #334155;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  padding: 16px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 12px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 0;
  color: #f8fafc;
}

.entity-label {
  margin: 0;
  color: #9db3c9;
  font-size: 12px;
}

.error-message {
  margin: 0;
  color: #fecaca;
  font-size: 12px;
  border: 1px solid rgba(248, 113, 113, 0.35);
  background: rgba(127, 29, 29, 0.35);
  border-radius: 8px;
  padding: 8px 10px;
}

header button {
  border: 1px solid #334155;
  border-radius: 7px;
  background: transparent;
  color: #9fb3c9;
  width: 30px;
  height: 30px;
}

.json-panel,
.table-panel {
  border: 1px solid #334155;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.75);
  overflow: auto;
}

pre {
  margin: 0;
  padding: 12px;
  color: #d6e5f6;
  font-size: 12px;
  line-height: 1.45;
}

.state-message {
  margin: 0;
  padding: 12px;
  color: #9db3c9;
  font-size: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid rgba(51, 65, 85, 0.65);
  text-align: left;
  padding: 8px;
  font-size: 12px;
}

th {
  color: #9db3c9;
}

td {
  color: #d6e5f6;
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
  color: #04220f;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
