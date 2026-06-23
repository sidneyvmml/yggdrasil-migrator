/**
 * Composable para gerenciar estado de UI global
 * Responsabilidade: navegação de abas, stepper, modos
 */
import { ref } from 'vue'
import { ActiveTab, MigrationMode } from '@/types/ui'

export const TABS = [
  { key: 'dashboard' as const, label: 'Dashboard' },
  { key: 'engines' as const, label: 'Engines' },
  { key: 'connections' as const, label: 'Connections' },
  { key: 'mapping' as const, label: 'Mapping' },
  { key: 'preview' as const, label: 'Preview' },
  { key: 'jobs' as const, label: 'Jobs' },
  { key: 'templates' as const, label: 'Templates' },
]

export const MIGRATION_FLOW_TABS = ['engines', 'connections', 'mapping', 'preview'] as const

export const MIGRATION_FLOW_TABS_FULL = [
  { key: 'engines' as const, label: 'Select Engines' },
  { key: 'connections' as const, label: 'Configure Connections' },
  { key: 'mapping' as const, label: 'Map Fields' },
  { key: 'preview' as const, label: 'Preview & Execute' },
]

export function useUI() {
  const activeTab = ref<ActiveTab>('dashboard')
  const migrationMode = ref<MigrationMode>('simple')

  /**
   * Define aba ativa
   */
  const setActiveTab = (tab: ActiveTab): void => {
    activeTab.value = tab
  }

  /**
   * Verifica se está no fluxo de migration
   */
  const isInMigrationFlow = (): boolean => {
    return MIGRATION_FLOW_TABS.includes(activeTab.value as any)
  }

  /**
   * Avança para próxima aba no fluxo de migration
   */
  const nextTab = (): void => {
    const currentIndex = MIGRATION_FLOW_TABS.indexOf(activeTab.value as any)
    if (currentIndex < MIGRATION_FLOW_TABS.length - 1) {
      setActiveTab(MIGRATION_FLOW_TABS[currentIndex + 1] as ActiveTab)
    }
  }

  /**
   * Volta para aba anterior no fluxo de migration
   */
  const previousTab = (): void => {
    const currentIndex = MIGRATION_FLOW_TABS.indexOf(activeTab.value as any)
    if (currentIndex > 0) {
      setActiveTab(MIGRATION_FLOW_TABS[currentIndex - 1] as ActiveTab)
    }
  }

  /**
   * Vai para aba específica no fluxo
   */
  const goToMigrationStep = (stepIndex: number): void => {
    if (stepIndex >= 0 && stepIndex < MIGRATION_FLOW_TABS.length) {
      setActiveTab(MIGRATION_FLOW_TABS[stepIndex] as ActiveTab)
    }
  }

  /**
   * Alterna modo de migration
   */
  const setMigrationMode = (mode: MigrationMode): void => {
    migrationMode.value = mode
  }

  /**
   * Reseta UI ao estado inicial
   */
  const resetUI = (): void => {
    activeTab.value = 'dashboard'
    migrationMode.value = 'simple'
  }

  return {
    activeTab,
    migrationMode,
    setActiveTab,
    isInMigrationFlow,
    nextTab,
    previousTab,
    goToMigrationStep,
    setMigrationMode,
    resetUI,
  }
}
