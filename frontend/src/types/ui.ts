/**
 * Tipos para estado de UI
 */

export type ActiveTab = 'dashboard' | 'engines' | 'connections' | 'mapping' | 'preview' | 'jobs' | 'templates'
export type MigrationMode = 'simple' | 'custom'
export type SortBy = 'date_desc' | 'date_asc'

export interface TabDefinition {
  key: ActiveTab
  label: string
}

export interface UiState {
  activeTab: ActiveTab
  migrationMode: MigrationMode
  createJobLoading: boolean
  templatesSaving: boolean
}

export interface PaginationState {
  currentPage: number
  pageSize: number
  totalPages: number
}

export interface JobsUIState extends PaginationState {
  sortBy: SortBy
  loading: boolean
  rerunLoadingId: string
  deleteLoadingId: string
}
