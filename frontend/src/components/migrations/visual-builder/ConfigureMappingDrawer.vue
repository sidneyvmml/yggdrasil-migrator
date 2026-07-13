<template>
  <aside :class="['mapping-drawer', { collapsed }]" aria-label="Configure Mapping Drawer">
    <header class="drawer-header">
      <div>
        <h3>Configure Mapping</h3>
        <p>{{ mappingTitle }}</p>
      </div>
      <div class="drawer-header-actions">
        <button
          type="button"
          class="close-btn"
          :aria-label="collapsed ? 'Expand mapping drawer' : 'Collapse mapping drawer'"
          @click="$emit('toggle-collapse')"
        >
          {{ collapsed ? '+' : '-' }}
        </button>
        <button type="button" class="close-btn" aria-label="Close mapping drawer" @click="$emit('close')">x</button>
      </div>
    </header>

    <template v-if="!collapsed">
      <nav class="tab-row" aria-label="Drawer tabs">
        <button class="tab active" type="button">Field Mapping</button>
        <button class="tab" type="button">Transformations</button>
      </nav>

      <FieldMappingTable :rows="rows" />

      <section v-if="validationText" class="validation-result">
        <h4>Validation Result</h4>
        <pre>{{ validationText }}</pre>
      </section>

      <footer class="drawer-actions">
        <button type="button" class="btn-secondary" @click="$emit('validate-mapping')">Validate Mapping</button>
        <button type="button" class="btn-primary" @click="$emit('save-mapping')">Save Mapping</button>
      </footer>
    </template>
    <p v-else class="collapsed-label">Drawer collapsed</p>
  </aside>
</template>

<script setup lang="ts">
import type { FieldMapping } from '@/mocks/visualMigrationBuilder.mock'
import FieldMappingTable from './FieldMappingTable.vue'

defineProps<{
  rows: FieldMapping[]
  mappingTitle: string
  validationText?: string
  collapsed?: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'toggle-collapse'): void
  (e: 'validate-mapping'): void
  (e: 'save-mapping'): void
}>()
</script>

<style scoped>
.mapping-drawer {
  width: 340px;
  min-width: 280px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #101b30 0%, #0f172a 100%);
  padding: 14px;
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 12px;
}

.mapping-drawer.collapsed {
  grid-template-rows: auto auto;
}

.drawer-header-actions {
  display: flex;
  gap: 6px;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.drawer-header h3 {
  margin: 0;
  color: #f8fafc;
}

.drawer-header p {
  margin: 4px 0 0;
  color: #9db1c8;
  font-size: 12px;
}

.close-btn {
  border: 1px solid #334155;
  border-radius: 8px;
  background: transparent;
  color: #94a3b8;
  width: 30px;
  height: 30px;
}

.collapsed-label {
  margin: 0;
  color: #9db3c9;
  font-size: 12px;
}

.tab-row {
  display: flex;
  gap: 8px;
}

.tab {
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #94a3b8;
  padding: 6px 2px;
  font-size: 12px;
}

.tab.active {
  color: #d8fbe5;
  border-color: #22c55e;
}

.drawer-actions {
  display: flex;
  gap: 8px;
}

.validation-result {
  border: 1px solid rgba(245, 158, 11, 0.45);
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.08);
  padding: 10px;
}

.validation-result h4 {
  margin: 0 0 6px;
  color: #f8fafc;
  font-size: 12px;
}

.validation-result pre {
  margin: 0;
  white-space: pre-wrap;
  color: #dbe8f8;
  font-size: 12px;
  line-height: 1.45;
}

.btn-secondary,
.btn-primary {
  flex: 1;
  border-radius: 8px;
  padding: 9px 10px;
  font-size: 12px;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid #334155;
  background: #0f172a;
  color: #d6e2f0;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #03210f;
}

@media (max-width: 1200px) {
  .mapping-drawer {
    width: 100%;
  }
}
</style>
