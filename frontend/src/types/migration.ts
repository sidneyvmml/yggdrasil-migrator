/**
 * Tipos para migration jobs e resultados
 */

export interface MigrationResult {
  processed: number
  inserted: number
  merged?: number
  skipped: number
  error?: string
  warning?: string
  warnings?: string[]
}

export interface JobItem {
  jobId: string
  sourceEngine: string
  targetEngine: string
  status: 'pending' | 'loading_source' | 'mapping_fields' | 'inserting_documents' | 'done' | 'failed'
  progress: number
  createdAt: string
  updatedAt: string
  result: MigrationResult | null
  canRerun: boolean
}

export interface MappingRow {
  sourceField: string
  targetField: string
  transformation: string
}

export interface PreviewSample {
  [key: string]: any
}

export interface TemplateItem {
  templateId: string
  name: string
  description?: string
  sourceEngine: string
  targetEngine: string
  config: any
  createdAt: string
  updatedAt: string
}
