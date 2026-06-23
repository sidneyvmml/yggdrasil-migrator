<template>
  <article class="engine-selector">
    <div class="engine-selector-header">
      <h2>Available Engines</h2>
      <p class="engine-selector-description">Select source and target engines for migration</p>
    </div>

    <div class="engines-grid">
      <article
        v-for="engine in engines"
        :key="engine.name"
        :class="[
          'engine-card',
          engine.available ? 'available' : 'disabled',
          isSelected(engine.name) ? 'selected' : '',
        ]"
      >
        <div class="engine-card-head">
          <div class="engine-brand-row">
            <img
              v-if="getEngineLogo(engine.name)"
              class="engine-brand-logo"
              :src="getEngineLogo(engine.name)"
              :alt="`${engine.name} logo`"
            />
            <span v-else class="engine-brand-glyph">{{ getEngineGlyph(engine.name) }}</span>
            <div class="engine-brand-text">
              <div class="engine-title-with-badge">
                <h4>{{ engine.name }}</h4>
                <span v-if="engine.name === 'Keycloak'" class="engine-badge">
                  Keycloak to Keycloak only
                </span>
              </div>
            </div>
          </div>
          <span :class="['wizard-status', engine.available ? 'valid' : 'warn']">
            {{ engine.available ? 'Available' : 'Coming soon' }}
          </span>
        </div>

        <p>{{ engine.type }}</p>
        <small>{{ engine.description }}</small>

        <div class="engine-tags">
          <span v-for="feature in engine.features" :key="feature">{{ feature }}</span>
        </div>

        <div class="engine-actions">
          <button
            :class="['wizard-secondary', 'engine-action-button', 'source', { active: selectedSourceEngine === engine.name }]"
            :disabled="!engine.selectable"
            @click="$emit('source-selected', engine.name)"
          >
            Set as Source
          </button>
          <button
            :class="['wizard-secondary', 'engine-action-button', 'target', { active: selectedTargetEngine === engine.name }]"
            :disabled="!engine.selectable"
            @click="$emit('target-selected', engine.name)"
          >
            Set as Target
          </button>
        </div>
      </article>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Engine, EngineType } from '@/types'
import { ENGINE_GLYPHS, ENGINE_LOGOS } from '@/composables/useEngine'

interface Props {
  /**
   * Lista de engines disponíveis
   */
  engines: Engine[]

  /**
   * Engine selecionado como source
   */
  selectedSourceEngine: EngineType | ''

  /**
   * Engine selecionado como target
   */
  selectedTargetEngine: EngineType | ''

  /**
   * URL base para logos
   */
  logoBasePath?: string
}

interface Emits {
  'source-selected': [engine: EngineType]
  'target-selected': [engine: EngineType]
}

const props = withDefaults(defineProps<Props>(), {
  logoBasePath: '/src/assets/',
})

defineEmits<Emits>()

/**
 * Verifica se um engine está selecionado
 */
const isSelected = (engineName: EngineType | string): boolean => {
  return engineName === props.selectedSourceEngine || engineName === props.selectedTargetEngine
}

/**
 * Retorna glyph do engine
 */
const getEngineGlyph = (engineName: string): string => {
  return ENGINE_GLYPHS[engineName] || '🗄'
}

/**
 * Retorna URL do logo do engine
 */
const getEngineLogo = (engineName: string): string => {
  const logoName = ENGINE_LOGOS[engineName]
  if (!logoName) return ''
  return new URL(`../assets/${logoName}`, import.meta.url).href
}
</script>

<style scoped>
.engine-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.engine-selector-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.engine-selector-description {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.engines-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.engine-card {
  border: 1px solid #334155;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  border-radius: 14px;
  padding: 14px;
  display: grid;
  gap: 10px;
  transition: all 0.2s ease;
}

.engine-card.available {
  cursor: pointer;
}

.engine-card.available:hover {
  border-color: #475569;
  background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.engine-card.selected {
  border-color: #22c55e;
  background: linear-gradient(180deg, #064e3b 0%, #0f172a 100%);
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

.engine-card.disabled {
  opacity: 0.66;
}

.engine-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.engine-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.engine-brand-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.engine-title-with-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.engine-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  background: rgba(147, 51, 234, 0.15);
  color: #d8b4fe;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid rgba(147, 51, 234, 0.3);
  white-space: nowrap;
}

.engine-brand-logo,
.engine-brand-glyph {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: rgba(15, 23, 42, 0.8);
  flex-shrink: 0;
}

.engine-brand-logo {
  object-fit: contain;
  padding: 3px;
}

.engine-brand-glyph {
  display: grid;
  place-items: center;
  font-size: 1rem;
}

.engine-card h4 {
  margin: 0;
  line-height: 1.2;
}

.engine-card p {
  margin: 0;
  color: #cbd5e1;
  font-size: 0.85rem;
}

.engine-card small {
  color: #94a3b8;
}

.engine-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.engine-tags span {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(59, 130, 246, 0.1);
  color: #93c5fd;
  font-size: 0.72rem;
  font-weight: 600;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.engine-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.engine-action-button {
  flex: 1;
  padding: 8px 12px;
  font-size: 0.8rem;
  margin-top: 0;
  border-radius: 8px;
  background: #1f2937;
  color: #cbd5e1;
  border: 1px solid #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.engine-action-button:hover:not(:disabled) {
  background: #334155;
  border-color: #475569;
}

.engine-action-button.active {
  background: #22c55e;
  color: #052e16;
  border-color: #22c55e;
  font-weight: 600;
}

.engine-action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.wizard-status {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.wizard-status.valid {
  background: rgba(34, 197, 94, 0.12);
  color: #10b981;
}

.wizard-status.warn {
  background: rgba(251, 146, 60, 0.12);
  color: #fb923c;
}
</style>
