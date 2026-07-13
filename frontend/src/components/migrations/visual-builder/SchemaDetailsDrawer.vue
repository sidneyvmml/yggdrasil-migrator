<template>
  <aside class="drawer" aria-label="Schema Details">
    <header>
      <h3>Schema Details</h3>
      <button type="button" aria-label="Close schema details" @click="$emit('close')">x</button>
    </header>

    <section class="content">
      <p><strong>Table:</strong> clients</p>
      <p><strong>Schema:</strong> public</p>
      <p><strong>Rows:</strong> 8,201</p>
      <p><strong>Columns:</strong> 14</p>

      <h4>Columns</h4>
      <pre>id          varchar      primary key, required
name_client varchar      required
document    varchar      unique, required
email       varchar      nullable
phone       varchar      nullable
city        varchar      nullable
state       varchar      nullable
zip_code    varchar      nullable
company_id  varchar      foreign key
created_at  timestamp    required
tags        jsonb        nullable
status      varchar      default active
is_active   boolean      default true
notes       text         nullable</pre>

      <h4>Constraints</h4>
      <ul>
        <li>clients_pkey</li>
        <li>clients_document_unique</li>
        <li>clients_company_fk</li>
      </ul>

      <h4>Indexes</h4>
      <ul>
        <li>idx_clients_document</li>
        <li>idx_clients_company_id</li>
      </ul>
    </section>

    <footer>
      <button type="button" class="btn-secondary" @click="$emit('close')">Close</button>
      <button type="button" class="btn-primary" @click="$emit('use-target')">Use as Target</button>
    </footer>
  </aside>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'close'): void
  (e: 'use-target'): void
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
  color: #9eb1c7;
  width: 30px;
  height: 30px;
}

.content {
  border: 1px solid #334155;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.76);
  padding: 12px;
  overflow: auto;
}

.content p,
.content li {
  color: #d4e4f6;
  font-size: 12px;
}

.content h4 {
  margin: 12px 0 8px;
  color: #f8fafc;
  font-size: 13px;
}

pre {
  margin: 0;
  color: #d6e5f7;
  font-size: 12px;
  line-height: 1.45;
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
  color: #d3e6f8;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #04220f;
}
</style>
