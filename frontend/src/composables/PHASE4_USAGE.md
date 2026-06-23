/**
 * FASE 4: Stepper Clicável e Botão Voltar
 *
 * Documentação de como usar stepper clicável e navegação entre abas
 */

/**
 * EXEMPLO DE USO NO APP.VUE
 *
 * 1. Importar composables
 */
import { useUI, MIGRATION_FLOW_TABS, TABS } from '@/composables/useUI'
import { Stepper } from '@/components'

/**
 * 2. Setup
 */
const ui = useUI()

/**
 * 3. NO TEMPLATE - Usar Stepper com clique habilitado
 */
/*
<Stepper
  :steps="migrationFlowTabs"
  :currentStep="getCurrentMigrationStep()"
  :allow-backtrack="true"
  @step-selected="goToMigrationStep"
/>
*/

/**
 * 4. MÉTODOS NECESSÁRIOS
 */

// Retorna o índice do passo atual no fluxo de migration
function getCurrentMigrationStep(): number {
  return MIGRATION_FLOW_TABS.indexOf(ui.activeTab.value as any)
}

// Vai para um passo específico
function goToMigrationStep(stepIndex: number): void {
  ui.goToMigrationStep(stepIndex)
}

// Volta para a aba anterior (Jobs, Dashboard, etc)
function goBack(): void {
  ui.setActiveTab('jobs')
}

// Avança para próximo passo no fluxo
function nextStep(): void {
  ui.nextTab()
}

// Volta para passo anterior no fluxo
function previousStep(): void {
  ui.previousTab()
}

/**
 * 5. NO TEMPLATE - Usar JobsList com botão voltar
 */
/*
<JobsList
  :jobs="jobs"
  :loading="loading"
  :current-page="currentPage"
  :page-size="pageSize"
  :sort-by="sortBy"
  @back="goBack()"
  @refresh="loadJobs(true)"
  @page-changed="setPage"
  @page-size-changed="setPageSize"
  @sort-changed="setSortBy"
/>
*/

/**
 * FEATURES HABILITADAS:
 *
 * 1. Stepper Clicável:
 *    - Usuário pode clicar em qualquer passo anterior para retroceder
 *    - Cada passo mostra seu status (pendente, ativo, completo)
 *    - Indicador visual de progresso
 *
 * 2. Botão Voltar em Jobs:
 *    - Volta para Dashboard ou aba anterior
 *    - Estado da joblist é preservado
 *    - Permite navegar sem perder contexto
 *
 * 3. Navegação Entre Abas:
 *    - nextTab() - Próximo passo do fluxo
 *    - previousTab() - Passo anterior do fluxo
 *    - goToMigrationStep(index) - Passo específico
 *    - setActiveTab(tab) - Qualquer aba
 *    - isInMigrationFlow() - Verifica se está no fluxo
 *
 * COMPOSABLE useUI:
 *    - activeTab: current active tab
 *    - migrationMode: 'simple' | 'custom'
 *    - setActiveTab(tab): navega para aba
 *    - nextTab(): próximo passo
 *    - previousTab(): passo anterior
 *    - goToMigrationStep(index): passo específico
 *    - isInMigrationFlow(): boolean
 *    - setMigrationMode(mode): alterna modo
 *    - resetUI(): reseta tudo
 */
