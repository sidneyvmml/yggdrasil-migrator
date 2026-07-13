export type DatabaseEngine = 'mongodb' | 'postgresql'

export type MappingVisualStatus = 'ready' | 'needs_review' | 'not_connected' | 'warning' | 'error'

export type MappingFieldStatus = 'valid' | 'warning' | 'ignored' | 'error'

export type DatabaseEntity = {
  id: string
  name: string
  engine: DatabaseEngine
  kind: 'collection' | 'table'
  recordsLabel: string
  fieldsCount: number
  metadata: string[]
  details: string[]
}

export type CanvasNode = {
  id: string
  entityId: string
  x: number
  y: number
  status: MappingVisualStatus
}

export type CanvasConnection = {
  id: string
  sourceNodeId: string
  targetNodeId: string
  label: string
  status: 'ready' | 'needs_review' | 'error'
  mappedFields?: number
  totalFields?: number
  subtitle?: string
}

export type FieldMapping = {
  id: string
  sourceField: string
  targetField: string
  transform: string
  status: MappingFieldStatus
}

export const sourceEntities: DatabaseEntity[] = [
  {
    id: 'src-accounts',
    name: 'accounts',
    engine: 'mongodb',
    kind: 'collection',
    recordsLabel: '124,392 documents',
    fieldsCount: 18,
    metadata: ['collection', 'objectId', 'arrays', 'DBRef'],
    details: ['Nested: 3', 'Arrays: 2', 'DBRefs: 1'],
  },
  {
    id: 'src-orders',
    name: 'orders',
    engine: 'mongodb',
    kind: 'collection',
    recordsLabel: '48,902 documents',
    fieldsCount: 23,
    metadata: ['collection', 'objectId', 'arrays', 'DBRef'],
    details: ['Nested: 2', 'Arrays: 3', 'DBRefs: 1'],
  },
  {
    id: 'src-users',
    name: 'users',
    engine: 'mongodb',
    kind: 'collection',
    recordsLabel: '22,120 documents',
    fieldsCount: 15,
    metadata: ['collection', 'objectId', 'arrays', 'DBRef'],
    details: ['Nested: 1', 'Arrays: 1', 'DBRefs: 0'],
  },
  {
    id: 'src-invoices',
    name: 'invoices',
    engine: 'mongodb',
    kind: 'collection',
    recordsLabel: '19,443 documents',
    fieldsCount: 31,
    metadata: ['collection', 'objectId', 'arrays', 'DBRef'],
    details: ['Nested: 3', 'Arrays: 4', 'DBRefs: 1'],
  },
  {
    id: 'src-products',
    name: 'products',
    engine: 'mongodb',
    kind: 'collection',
    recordsLabel: '9,800 documents',
    fieldsCount: 12,
    metadata: ['collection', 'objectId', 'arrays', 'DBRef'],
    details: ['Nested: 1', 'Arrays: 1', 'DBRefs: 0'],
  },
]

export const targetEntities: DatabaseEntity[] = [
  {
    id: 'tgt-clients',
    name: 'clients',
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '8,201 rows',
    fieldsCount: 14,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['8 required', '3 constraints', '2 indexes'],
  },
  {
    id: 'tgt-sales-orders',
    name: 'sales_orders',
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '48,902 rows',
    fieldsCount: 21,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['0 required', '5 constraints', '3 indexes'],
  },
  {
    id: 'tgt-app-users',
    name: 'app_users',
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '22,120 rows',
    fieldsCount: 16,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['5 required', '4 constraints', '1 indexes'],
  },
  {
    id: 'tgt-invoices',
    name: 'invoices',
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '0 rows',
    fieldsCount: 24,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['2 required', '2 constraints', '2 indexes'],
  },
  {
    id: 'tgt-products',
    name: 'products',
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '9,800 rows',
    fieldsCount: 12,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['1 required', '2 constraints', '1 indexes'],
  },
]

export const canvasNodes: CanvasNode[] = [
  { id: 'node-src-accounts', entityId: 'src-accounts', x: 40, y: 44, status: 'needs_review' },
  { id: 'node-tgt-clients', entityId: 'tgt-clients', x: 468, y: 44, status: 'needs_review' },
  { id: 'node-src-orders', entityId: 'src-orders', x: 40, y: 252, status: 'ready' },
  { id: 'node-tgt-sales-orders', entityId: 'tgt-sales-orders', x: 468, y: 252, status: 'ready' },
  { id: 'node-src-users', entityId: 'src-users', x: 40, y: 460, status: 'not_connected' },
]

export const canvasConnections: CanvasConnection[] = [
  {
    id: 'conn-accounts-clients',
    sourceNodeId: 'node-src-accounts',
    targetNodeId: 'node-tgt-clients',
    label: 'accounts -> clients',
    status: 'needs_review',
    mappedFields: 12,
    totalFields: 14,
    subtitle: 'Needs review',
  },
  {
    id: 'conn-orders-sales-orders',
    sourceNodeId: 'node-src-orders',
    targetNodeId: 'node-tgt-sales-orders',
    label: 'orders -> sales_orders',
    status: 'ready',
    subtitle: 'Mapping ready',
  },
]

export const fieldMappings: FieldMapping[] = [
  { id: '1', sourceField: '_id', targetField: 'id', transform: 'ObjectId to String', status: 'valid' },
  { id: '2', sourceField: 'name', targetField: 'name_client', transform: 'None', status: 'valid' },
  { id: '3', sourceField: 'documentId', targetField: 'document', transform: 'None', status: 'valid' },
  { id: '4', sourceField: 'address.city', targetField: 'city', transform: 'Extract', status: 'valid' },
  { id: '5', sourceField: 'address.state', targetField: 'state', transform: 'Extract', status: 'valid' },
  { id: '6', sourceField: 'zipCode', targetField: 'zip_code', transform: 'None', status: 'valid' },
  { id: '7', sourceField: 'company.$id', targetField: 'company_id', transform: 'DBRef Resolve', status: 'warning' },
  { id: '8', sourceField: 'createdAt', targetField: 'created_at', transform: 'Date Format', status: 'valid' },
  { id: '9', sourceField: 'status', targetField: 'status', transform: 'None', status: 'valid' },
  { id: '10', sourceField: 'tags', targetField: 'tags', transform: 'Array to JSON', status: 'valid' },
  { id: '11', sourceField: 'notes', targetField: 'notes', transform: 'None', status: 'valid' },
  { id: '12', sourceField: 'phone', targetField: 'phone', transform: 'None', status: 'valid' },
  { id: '13', sourceField: 'email', targetField: 'email', transform: 'None', status: 'valid' },
  { id: '14', sourceField: '_class', targetField: '_class', transform: 'None', status: 'ignored' },
]

export const flowValidationItems = [
  { id: 'fm', label: '2', description: 'entity mappings configured', tone: 'valid' as const },
  { id: 'nc', label: '1', description: 'entity not connected', tone: 'neutral' as const },
  { id: 'fd', label: '38', description: 'fields mapped', tone: 'valid' as const },
  { id: 'rt', label: '3', description: 'required target fields missing', tone: 'warning' as const },
  { id: 'db', label: '1', description: 'DBRef needs manual configuration', tone: 'warning' as const },
  { id: 'ce', label: '0', description: 'critical errors', tone: 'valid' as const },
]

export const executionPlan = {
  steps: ['accounts -> clients', 'orders -> sales_orders'],
  strategy: 'Dependency-based',
  estimatedRecords: '173,294',
}
