<template>
  <aside class="drawer" aria-label="Flow Validation Details">
    <header>
      <h3>Flow Validation Details</h3>
      <button type="button" aria-label="Close validation details" @click="$emit('close')">x</button>
    </header>

    <section class="content">
      <h4>Validation Summary</h4>
      <ul>
        <li>Source connection is healthy</li>
        <li>Target connection is healthy</li>
        <li>2 entity mappings configured</li>
        <li>38 fields mapped</li>
        <li>3 required target fields missing</li>
        <li>1 DBRef needs manual configuration</li>
        <li>0 critical errors</li>
      </ul>

      <h4>accounts -> clients</h4>
      <p>Status: Needs review</p>
      <ul>
        <li>company.$id requires DBRef configuration</li>
        <li>2 required fields are unmapped</li>
      </ul>

      <h4>orders -> sales_orders</h4>
      <p>Status: Ready</p>
      <p>No issues found.</p>

      <h4>users</h4>
      <p>Status: Not connected</p>
      <ul>
        <li>Entity is on canvas but not connected.</li>
      </ul>
    </section>

    <footer>
      <button type="button" class="btn-secondary" @click="$emit('close')">Close</button>
      <button type="button" class="btn-secondary" @click="$emit('run-dry-test')">Run Dry Test</button>
      <button type="button" class="btn-primary" @click="$emit('adjust-mapping')">Adjust Mapping</button>
    </footer>
  </aside>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'close'): void
  (e: 'run-dry-test'): void
  (e: 'adjust-mapping'): void
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

header button {
  border: 1px solid #334155;
  border-radius: 7px;
  background: transparent;
  color: #9fb3ca;
  width: 30px;
  height: 30px;
}

.content {
  border: 1px solid #334155;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.75);
  padding: 12px;
  overflow: auto;
}

.content h4 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 13px;
}

.content p,
.content li {
  color: #d4e5f6;
  font-size: 12px;
}

.content ul {
  margin: 0 0 10px;
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
  color: #d4e6f9;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #05220f;
}
</style>
