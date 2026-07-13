<template>
  <aside class="drawer" aria-label="Dry Run Results">
    <header>
      <h3>Dry Run Results</h3>
      <button type="button" aria-label="Close dry run" @click="$emit('close')">x</button>
    </header>

    <p v-if="running" class="running">Running dry test...</p>

    <template v-else>
      <p class="status">Status: Completed with warnings</p>
      <ul class="summary-list">
        <li>Tested records: 100</li>
        <li>Valid records: 94</li>
        <li>Failed records: 6</li>
        <li>Estimated full migration: 173,294 records</li>
      </ul>

      <section class="warnings">
        <h4>Warnings</h4>
        <ul>
          <li>3 required target fields are missing</li>
          <li>1 DBRef requires manual configuration</li>
          <li>6 records contain invalid date format</li>
        </ul>
      </section>

      <section v-if="showFailedRecords" class="failed-list">
        <h4>Failed Records</h4>
        <ul>
          <li v-for="item in failedRecords" :key="item">{{ item }}</li>
        </ul>
      </section>
    </template>

    <footer>
      <button type="button" class="btn-secondary" @click="$emit('toggle-failed-records')">View Failed Records</button>
      <button type="button" class="btn-secondary" @click="$emit('adjust-mapping')">Adjust Mapping</button>
      <button type="button" class="btn-secondary" @click="$emit('run-again')">Run Again</button>
      <button type="button" class="btn-primary" @click="$emit('continue-review')">Continue to Review</button>
    </footer>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  running: boolean
  showFailedRecords: boolean
  failedRecords: string[]
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'toggle-failed-records'): void
  (e: 'adjust-mapping'): void
  (e: 'run-again'): void
  (e: 'continue-review'): void
}>()
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
  overflow: auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h3 {
  margin: 0;
  color: #f8fafc;
}

header button {
  border: 1px solid #334155;
  border-radius: 7px;
  background: transparent;
  color: #a3b6cc;
  width: 30px;
  height: 30px;
}

.running,
.status {
  margin: 0;
  color: #f8fafc;
  font-weight: 600;
}

.summary-list,
.warnings ul,
.failed-list ul {
  margin: 0;
  padding-left: 18px;
  color: #c6d7ea;
  display: grid;
  gap: 6px;
}

.warnings,
.failed-list {
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 10px;
  background: rgba(15, 23, 42, 0.7);
}

.warnings h4,
.failed-list h4 {
  margin: 0 0 8px;
  color: #f8fafc;
}

footer {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn-secondary,
.btn-primary {
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid #334155;
  background: #0f172a;
  color: #d5e5f6;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #04210f;
}
</style>
