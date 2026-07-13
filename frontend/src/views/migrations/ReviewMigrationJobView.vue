<template>
  <section class="review-view">
    <header>
      <h2>Review Migration Job</h2>
      <p>Review source, target, mappings, validation and execution strategy before creating the migration job.</p>
    </header>

    <article class="card">
      <h3>Source and Target</h3>
      <p>Source: MongoDB / source_db</p>
      <p>Target: PostgreSQL / target_db</p>
    </article>

    <article class="card">
      <h3>Entity Mappings</h3>
      <p>accounts -> clients</p>
      <p>Status: Needs review</p>
      <p>Mapped fields: 12/14</p>
      <br />
      <p>orders -> sales_orders</p>
      <p>Status: Ready</p>
      <p>Mapped fields: 21/21</p>
    </article>

    <article class="card">
      <h3>Execution Summary</h3>
      <p>Estimated records: 173,294</p>
      <p>Strategy: Dependency-based</p>
      <p>Batch size: 1000</p>
      <p>Error handling: Skip failed records and list at the end</p>
    </article>

    <article class="card">
      <h3>Validation Summary</h3>
      <p>2 entity mappings configured</p>
      <p>1 warning</p>
      <p>0 critical errors</p>
    </article>

    <footer>
      <button type="button" class="btn-secondary" @click="$emit('back-builder')">Back to Builder</button>
      <button type="button" class="btn-secondary" @click="$emit('run-dry-test')">Run Dry Test</button>
      <button type="button" class="btn-primary" @click="$emit('create-job')">Create Migration Job</button>
    </footer>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'back-builder'): void
  (e: 'run-dry-test'): void
  (e: 'create-job'): void
}>()
</script>

<style scoped>
.review-view {
  display: grid;
  gap: 12px;
}

header h2,
header p,
h3,
p {
  margin: 0;
}

header h2,
h3 {
  color: #f8fafc;
}

header p,
p {
  color: #d4e5f6;
  font-size: 13px;
}

.card {
  border: 1px solid #334155;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.8);
  padding: 14px;
  display: grid;
  gap: 6px;
}

footer {
  display: flex;
  flex-wrap: wrap;
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
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #05220f;
}
</style>
