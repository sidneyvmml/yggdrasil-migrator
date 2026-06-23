<template>
  <button
    class="theme-switcher"
    :title="`Switch to ${isDark ? 'light' : 'dark'} mode`"
    :aria-label="`Switch to ${isDark ? 'light' : 'dark'} mode`"
    @click="toggleTheme"
  >
    <span v-if="isDark" class="theme-icon">🌙</span>
    <span v-else class="theme-icon">☀️</span>
    <span class="theme-label">{{ isDark ? 'Dark' : 'Light' }}</span>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables'

const { currentTheme, isDark, isLight, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #111827;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

[data-theme='light'] .theme-switcher {
  border-color: #cbd5e1;
  background: #f1f5f9;
  color: #1e293b;
}

.theme-switcher:hover {
  border-color: #475569;
  background: #1f2937;
}

[data-theme='light'] .theme-switcher:hover {
  border-color: #94a3b8;
  background: #e2e8f0;
}

.theme-icon {
  font-size: 1rem;
  display: inline-block;
}

.theme-label {
  display: none;
}

@media (min-width: 640px) {
  .theme-label {
    display: inline;
  }
}
</style>
