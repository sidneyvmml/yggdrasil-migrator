<template>
  <aside :class="['explorer-panel', { collapsed }]">
    <header class="panel-header">
      <div>
        <h3>{{ title }}</h3>
        <p>{{ subtitle }}</p>
      </div>

      <div class="panel-actions">
        <button
          v-if="canCollapse"
          type="button"
          class="icon-btn"
          :aria-label="collapsed ? `Expand ${title}` : `Collapse ${title}`"
          @click="$emit('toggle-collapse')"
        >
          {{ collapsed ? '+' : '-' }}
        </button>
        <button
          v-if="canClose"
          type="button"
          class="icon-btn"
          :aria-label="`Close ${title}`"
          @click="$emit('close')"
        >
          x
        </button>
      </div>
    </header>

    <template v-if="!collapsed">
      <label class="search-wrap">
        <span class="sr-only">{{ searchPlaceholder }}</span>
        <input type="text" :placeholder="searchPlaceholder" />
      </label>

      <button v-if="showCreateButton" class="create-button" type="button" @click="$emit('create-target-table')">+ Create target table</button>

      <div class="entity-list">
        <DatabaseEntityListItem
          v-for="entity in entities"
          :key="entity.id"
          :entity="entity"
          @add-to-canvas="$emit('add-entity', $event)"
        />
      </div>
    </template>
    <p v-else class="collapsed-label">Panel collapsed</p>
  </aside>
</template>

<script setup lang="ts">
import type { DatabaseEntity } from '@/mocks/visualMigrationBuilder.mock'
import DatabaseEntityListItem from './DatabaseEntityListItem.vue'

defineProps<{
  title: string
  subtitle: string
  searchPlaceholder: string
  entities: DatabaseEntity[]
  showCreateButton?: boolean
  collapsed?: boolean
  canCollapse?: boolean
  canClose?: boolean
}>()

defineEmits<{
  (e: 'create-target-table'): void
  (e: 'toggle-collapse'): void
  (e: 'close'): void
  (e: 'add-entity', entityId: string): void
}>()
</script>

<style scoped>
.explorer-panel {
  display: grid;
  grid-template-rows: auto auto auto 1fr;
  gap: 12px;
  min-height: 0;
  border: 1px solid #334155;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.8);
  padding: 14px;
}

.explorer-panel.collapsed {
  grid-template-rows: auto auto;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.panel-actions {
  display: flex;
  gap: 6px;
}

.icon-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: 1px solid #334155;
  background: transparent;
  color: #9fb3c9;
  font-weight: 700;
}

header h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 16px;
}

header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.search-wrap input {
  width: 90%;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #d9e6f5;
  padding: 8px 10px;
  font-size: 12px;
}

.create-button {
  border: 1px solid rgba(6, 182, 212, 0.45);
  border-radius: 8px;
  background: rgba(6, 182, 212, 0.1);
  color: #67e8f9;
  font-size: 12px;
  font-weight: 600;
  padding: 8px 10px;
  text-align: left;
}

.entity-list {
  overflow: auto;
  display: grid;
  align-content: start;
  gap: 10px;
  min-height: 0;
}

.collapsed-label {
  margin: 0;
  color: #9db3c9;
  font-size: 12px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
