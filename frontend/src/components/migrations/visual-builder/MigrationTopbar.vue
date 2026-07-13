<template>
  <header class="builder-topbar">
    <div class="left">
      <button type="button" class="icon-btn" @click="$emit('back')" aria-label="Back to previous step"><span aria-hidden="true">Back</span></button>
      <p class="breadcrumb">New Migration / Visual Builder</p>
    </div>

    <div class="actions">
      <button type="button" class="btn-secondary" @click="$emit('save-draft')">Save Draft</button>
      <button type="button" class="btn-secondary" @click="$emit('run-dry-test')">Run Dry Test</button>
      <button type="button" class="btn-primary" @click="$emit('continue')">Continue to Review</button>
    </div>
  </header>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'back'): void
  (e: 'save-draft'): void
  (e: 'run-dry-test'): void
  (e: 'continue'): void
}>()
</script>

<style scoped>
.builder-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  width: 50px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0b1220;
  color: #d4e6f9;
}

.breadcrumb {
  margin: 0;
  font-size: 14px;
  color: #e2e8f0;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-secondary,
.btn-primary {
  border-radius: 8px;
  padding: 8px 11px;
  font-size: 12px;
  font-weight: 600;
}

.btn-secondary {
  border: 1px solid #334155;
  background: #0f172a;
  color: #d5e5f7;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.5);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #03210f;
}
</style>
