/**
 * Composable para gerenciar engines
 * Responsabilidade: seleção de engines, compatibilidade, validação
 */
import { ref, computed } from 'vue'
import { EngineType } from '@/types/engine'

export const ENGINE_DEFINITIONS = [
  {
    name: 'MongoDB',
    type: 'Document database',
    description: 'Collections, nested objects, arrays, DBRef, ObjectId',
    features: ['Collections', 'Nested Objects', 'DBRef'],
    available: true,
    selectable: true,
  },
  {
    name: 'PostgreSQL',
    type: 'Relational database',
    description: 'Schemas, tables, columns, primary keys, constraints',
    features: ['Schemas', 'Constraints', 'JSONB'],
    available: true,
    selectable: true,
  },
  {
    name: 'Keycloak',
    type: 'Identity and Access Management',
    description: 'Realm users migration with configurable field mapping (Keycloak to Keycloak only)',
    features: ['Users', 'Realms', 'Username mapping'],
    available: true,
    selectable: true,
  },
  {
    name: 'MySQL',
    type: 'Relational database',
    description: 'Coming soon',
    features: ['Tables', 'Indexes'],
    available: false,
    selectable: false,
  },
  {
    name: 'Oracle',
    type: 'Enterprise relational database',
    description: 'Coming soon',
    features: ['Enterprise', 'PL/SQL'],
    available: false,
    selectable: false,
  },
  {
    name: 'Redis',
    type: 'Key-value database',
    description: 'Coming soon',
    features: ['KV', 'Streams'],
    available: false,
    selectable: false,
  },
]

export const ENGINE_GLYPHS: Record<string, string> = {
  MongoDB: '🍃',
  PostgreSQL: '🐘',
  MySQL: '🐬',
  Oracle: '◉',
  Keycloak: '🛡',
  Redis: '🧠',
}

export const ENGINE_LOGOS: Record<string, string> = {
  MongoDB: 'MongoDB.png',
  PostgreSQL: 'postgres.png',
  Redis: 'redis.png',
}

export function useEngine() {
  const selectedSourceEngine = ref<EngineType | ''>('MongoDB')
  const selectedTargetEngine = ref<EngineType | ''>('MongoDB')

  const selectableEngineNames = computed(() => {
    return ENGINE_DEFINITIONS.filter((engine) => engine.selectable).map((engine) => engine.name)
  })

  /**
   * Valida compatibilidade de engines
   * Keycloak só pode migrar para Keycloak
   */
  const isCompatible = computed(() => {
    if (!selectedSourceEngine.value || !selectedTargetEngine.value) {
      return false
    }

    const hasKeycloak =
      selectedSourceEngine.value === 'Keycloak' || selectedTargetEngine.value === 'Keycloak'

    if (!hasKeycloak) {
      return true
    }

    return selectedSourceEngine.value === 'Keycloak' && selectedTargetEngine.value === 'Keycloak'
  })

  /**
   * Define engine de origem
   */
  const setSourceEngine = (engineName: EngineType | ''): void => {
    if (engineName && !selectableEngineNames.value.includes(engineName)) {
      return
    }

    selectedSourceEngine.value = engineName

    if (engineName === 'Keycloak') {
      selectedTargetEngine.value = 'Keycloak'
    } else {
      if (selectedTargetEngine.value === 'Keycloak') {
        selectedTargetEngine.value = ''
      }
    }
  }

  /**
   * Define engine de destino
   */
  const setTargetEngine = (engineName: EngineType | ''): void => {
    if (engineName && !selectableEngineNames.value.includes(engineName)) {
      return
    }

    selectedTargetEngine.value = engineName

    if (engineName === 'Keycloak') {
      selectedSourceEngine.value = 'Keycloak'
    } else {
      if (selectedSourceEngine.value === 'Keycloak') {
        selectedSourceEngine.value = ''
      }
    }
  }

  /**
   * Retorna glyph do engine
   */
  const getEngineGlyph = (engineName: string): string => ENGINE_GLYPHS[engineName] || '🗄'

  /**
   * Retorna nome do arquivo de logo do engine
   */
  const getEngineLogo = (engineName: string): string => ENGINE_LOGOS[engineName] || ''

  return {
    selectedSourceEngine,
    selectedTargetEngine,
    selectableEngineNames,
    isCompatible,
    setSourceEngine,
    setTargetEngine,
    getEngineGlyph,
    getEngineLogo,
  }
}
