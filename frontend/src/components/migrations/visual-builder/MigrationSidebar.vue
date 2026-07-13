<template>
  <aside class="migration-sidebar">
    <h3>New Migration</h3>
    <ul>
      <li class="active">Visual Builder</li>
      <li>Configure Connections</li>
      <li>Field Mapping</li>
      <li>Preview</li>
      <li>Execute</li>
    </ul>
  </aside>
</template>

<style scoped>
.migration-sidebar {
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px;
  background: rgba(11, 18, 32, 0.75);
}

h3 {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 13px;
}

ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

li {
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 6px 8px;
  color: #9cb1c9;
  font-size: 12px;
}

li.active {
  border-color: rgba(34, 197, 94, 0.5);
  color: #b6f8cf;
  background: rgba(34, 197, 94, 0.1);
}
</style>
