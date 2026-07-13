<template>
  <section class="visual-builder-view">
    <template v-if="isReviewViewOpen">
      <p class="route-path">/new-migration/review</p>
      <ReviewMigrationJobView
        @back-builder="isReviewViewOpen = false"
        @run-dry-test="openDryRun"
        @create-job="isCreateJobConfirmOpen = true"
      />
    </template>

    <template v-else>
      <MigrationTopbar
        @back="$emit('back')"
        @save-draft="isSaveDraftModalOpen = true"
        @run-dry-test="openDryRun"
        @continue="isReviewViewOpen = true"
      />

      <ConnectionStatusBar
        :source-engine="props.sourceEngine"
        :target-engine="props.targetEngine"
        :source-database="props.sourceDatabase"
        :target-database="props.targetDatabase"
      />

      <div :class="['main-grid', { 'no-source': !isSourceExplorerOpen }]">
        <DatabaseExplorerPanel
          v-if="isSourceExplorerOpen"
          title="Source Explorer"
          :subtitle="`${props.sourceEngine} ${props.sourceDatabase}`"
          search-placeholder="Search collections..."
          :entities="sourceEntityList"
          :collapsed="isSourceExplorerCollapsed"
          :can-collapse="true"
          :can-close="true"
          @toggle-collapse="isSourceExplorerCollapsed = !isSourceExplorerCollapsed"
          @close="isSourceExplorerOpen = false"
          @add-entity="addEntityToCanvas"
        />

        <div class="canvas-column">
          <div class="canvas-column-controls">
            <button v-if="!isSourceExplorerOpen" type="button" class="panel-toggle" @click="isSourceExplorerOpen = true">Open Source Explorer</button>
            <button v-if="!isTargetExplorerOpen" type="button" class="panel-toggle" @click="isTargetExplorerOpen = true">Open Target Explorer</button>
            <button v-if="!isConfigureMappingDrawerOpen" type="button" class="panel-toggle" @click="isConfigureMappingDrawerOpen = true">Open Mapping Drawer</button>
          </div>

          <MigrationCanvas
            :active-mode="activeMode"
            :zoom-percent="canvasZoom"
            :selected-node-id="selectedNodeId"
            :connect-source-node-id="selectedNodeForConnect?.id || null"
            :nodes="canvasNodeList"
            :entities="allEntities"
            :connections="canvasConnectionList"
            :plan="executionPlanData"
            @select-mode="enableSelectMode"
            @connect-mode="enableConnectMode"
            @auto-layout="applyAutoLayout"
            @validate-flow="isFlowValidationDrawerOpen = true"
            @clear-canvas="isClearCanvasModalOpen = true"
            @zoom-in="zoomIn"
            @zoom-out="zoomOut"
            @reset-zoom="resetZoom"
            @fit-view="fitView"
            @node-selected="onNodeSelected"
            @preview-node="openPreview"
            @map-fields="openMapFields"
            @schema-details="isSchemaDetailsDrawerOpen = true"
            @drop-entity="onDropEntity"
            @move-node="onMoveNode"
          />
        </div>

        <aside class="right-rail">
          <DatabaseExplorerPanel
            v-if="isTargetExplorerOpen"
            title="Target Explorer"
            :subtitle="`${props.targetEngine} ${props.targetDatabase}`"
            search-placeholder="Search tables..."
            :entities="targetEntityList"
            :show-create-button="true"
            :collapsed="isTargetExplorerCollapsed"
            :can-collapse="true"
            :can-close="true"
            @create-target-table="isCreateTargetTableModalOpen = true"
            @toggle-collapse="isTargetExplorerCollapsed = !isTargetExplorerCollapsed"
            @close="isTargetExplorerOpen = false"
            @add-entity="addEntityToCanvas"
          />

          <ConfigureMappingDrawer
            v-if="isConfigureMappingDrawerOpen"
            :rows="fieldMappingRows"
            :mapping-title="selectedMappingTitle"
            :validation-text="mappingValidationText"
            :collapsed="isConfigureMappingDrawerCollapsed"
            @close="isConfigureMappingDrawerOpen = false"
            @toggle-collapse="isConfigureMappingDrawerCollapsed = !isConfigureMappingDrawerCollapsed"
            @validate-mapping="validateMapping"
            @save-mapping="saveMapping"
          />
        </aside>
      </div>

      <FlowValidationBar :items="flowValidationItems" @open-details="isFlowValidationDrawerOpen = true" />
    </template>

    <SaveDraftModal
      v-if="isSaveDraftModalOpen"
      v-model:draft-name="draftName"
      v-model:description="draftDescription"
      @cancel="isSaveDraftModalOpen = false"
      @save="saveDraft"
    />

    <DryRunResultsDrawer
      v-if="isDryRunDrawerOpen"
      :running="isDryRunRunning"
      :show-failed-records="showFailedRecords"
      :failed-records="failedRecords"
      @close="isDryRunDrawerOpen = false"
      @toggle-failed-records="showFailedRecords = !showFailedRecords"
      @adjust-mapping="adjustMappingFromDryRun"
      @run-again="runDryTestAgain"
      @continue-review="continueToReview"
    />

    <CreateTargetTableModal
      v-if="isCreateTargetTableModalOpen"
      :form="createTableForm"
      @update:field="updateCreateTableField"
      @cancel="isCreateTargetTableModalOpen = false"
      @create-table="createTargetTable"
    />

    <DataPreviewDrawer
      v-if="isDataPreviewDrawerOpen"
      :kind="previewKind"
      :entity-name="previewEntityName"
      :mongo-sample="previewMongoSample"
      :table-columns="previewTableColumns"
      :table-rows="previewTableRows"
      :loading="previewLoading"
      :error-message="previewError"
      @close="isDataPreviewDrawerOpen = false"
      @map-fields="openMapFieldsFromPreview"
    />

    <SchemaDetailsDrawer
      v-if="isSchemaDetailsDrawerOpen"
      @close="isSchemaDetailsDrawerOpen = false"
      @use-target="useAsTarget"
    />

    <FlowValidationDrawer
      v-if="isFlowValidationDrawerOpen"
      @close="isFlowValidationDrawerOpen = false"
      @run-dry-test="openDryRun"
      @adjust-mapping="adjustMappingFromValidation"
    />

    <ClearCanvasConfirmModal
      v-if="isClearCanvasModalOpen"
      @cancel="isClearCanvasModalOpen = false"
      @clear-canvas="clearCanvas"
    />

    <CreateMigrationMappingModal
      v-if="isCreateMappingModalOpen"
      :source-label="connectSourceLabel"
      :target-label="connectTargetLabel"
      @cancel="isCreateMappingModalOpen = false"
      @configure-mapping="confirmCreateMapping"
    />

    <div v-if="isCreateJobConfirmOpen" class="inline-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="create-job-title">
      <div class="inline-modal-card">
        <h3 id="create-job-title">Create Migration Job?</h3>
        <p>This will create a migration job based on the current visual flow.</p>
        <footer>
          <button type="button" class="btn-secondary" @click="isCreateJobConfirmOpen = false">Cancel</button>
          <button type="button" class="btn-primary" @click="createMigrationJob">Create Job</button>
        </footer>
      </div>
    </div>

    <ActionToast :visible="toastVisible" :message="toastMessage" />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { apiClient } from '@/services/api'
import {
  flowValidationItems as flowValidationItemsMock,
  type CanvasConnection,
  type CanvasNode,
  type DatabaseEntity,
  type FieldMapping,
} from '@/mocks/visualMigrationBuilder.mock'
import MigrationTopbar from '@/components/migrations/visual-builder/MigrationTopbar.vue'
import ConnectionStatusBar from '@/components/migrations/visual-builder/ConnectionStatusBar.vue'
import DatabaseExplorerPanel from '@/components/migrations/visual-builder/DatabaseExplorerPanel.vue'
import MigrationCanvas from '@/components/migrations/visual-builder/MigrationCanvas.vue'
import ConfigureMappingDrawer from '@/components/migrations/visual-builder/ConfigureMappingDrawer.vue'
import FlowValidationBar from '@/components/migrations/visual-builder/FlowValidationBar.vue'
import SaveDraftModal from '@/components/migrations/visual-builder/SaveDraftModal.vue'
import DryRunResultsDrawer from '@/components/migrations/visual-builder/DryRunResultsDrawer.vue'
import CreateTargetTableModal from '@/components/migrations/visual-builder/CreateTargetTableModal.vue'
import type { CreateTableForm } from '@/components/migrations/visual-builder/CreateTargetTableModal.vue'
import DataPreviewDrawer from '@/components/migrations/visual-builder/DataPreviewDrawer.vue'
import SchemaDetailsDrawer from '@/components/migrations/visual-builder/SchemaDetailsDrawer.vue'
import FlowValidationDrawer from '@/components/migrations/visual-builder/FlowValidationDrawer.vue'
import ClearCanvasConfirmModal from '@/components/migrations/visual-builder/ClearCanvasConfirmModal.vue'
import CreateMigrationMappingModal from '@/components/migrations/visual-builder/CreateMigrationMappingModal.vue'
import ActionToast from '@/components/migrations/visual-builder/ActionToast.vue'
import ReviewMigrationJobView from '@/views/migrations/ReviewMigrationJobView.vue'

const props = withDefaults(defineProps<{
  sourceEngine?: string
  targetEngine?: string
  sourceDatabase?: string
  targetDatabase?: string
  sourceEntityNames?: string[]
  targetEntityNames?: string[]
  sourceSamples?: Record<string, any>[]
  targetSamples?: Record<string, any>[]
  sourceConnection?: {
    connectionString?: string
    database?: string
    authEnabled?: boolean
    username?: string
    password?: string
    authSource?: string
  }
  targetConnection?: {
    connectionString?: string
    database?: string
    authEnabled?: boolean
    username?: string
    password?: string
    authSource?: string
  }
}>(), {
  sourceEngine: 'MongoDB',
  targetEngine: 'PostgreSQL',
  sourceDatabase: 'source_db',
  targetDatabase: 'target_db',
  sourceEntityNames: () => [],
  targetEntityNames: () => [],
  sourceSamples: () => [],
  targetSamples: () => [],
  sourceConnection: () => ({}),
  targetConnection: () => ({}),
})

defineEmits<{ (e: 'back'): void; (e: 'continue'): void }>()

const activeMode = ref<'select' | 'connect'>('select')

const isSaveDraftModalOpen = ref(false)
const isDryRunDrawerOpen = ref(false)
const isCreateTargetTableModalOpen = ref(false)
const isDataPreviewDrawerOpen = ref(false)
const isSchemaDetailsDrawerOpen = ref(false)
const isFlowValidationDrawerOpen = ref(false)
const isClearCanvasModalOpen = ref(false)
const isCreateMappingModalOpen = ref(false)
const isConfigureMappingDrawerOpen = ref(false)
const isConfigureMappingDrawerCollapsed = ref(false)
const isReviewViewOpen = ref(false)
const isCreateJobConfirmOpen = ref(false)
const isSourceExplorerOpen = ref(true)
const isSourceExplorerCollapsed = ref(false)
const isTargetExplorerOpen = ref(true)
const isTargetExplorerCollapsed = ref(false)

const sourceEntityList = ref<DatabaseEntity[]>([])
const targetEntityList = ref<DatabaseEntity[]>([])
const canvasNodeList = ref<CanvasNode[]>([])
const canvasConnectionList = ref<CanvasConnection[]>([])
const fieldMappingRows = ref<FieldMapping[]>([])

const allEntities = computed(() => [...sourceEntityList.value, ...targetEntityList.value])
const executionPlanData = computed(() => {
  const steps = canvasConnectionList.value.map((item) => item.label)
  return {
    steps,
    strategy: steps.length > 0 ? 'Connection-based' : 'Awaiting mapping',
    estimatedRecords: steps.length > 0 ? `${steps.length} mapping(s)` : '--',
  }
})

const flowValidationItems = flowValidationItemsMock

const selectedNodeForConnect = ref<CanvasNode | null>(null)
const pendingTargetNode = ref<CanvasNode | null>(null)
const selectedNodeId = ref<string | null>(null)
const canvasZoom = ref(100)
const connectSourceLabel = ref(`${props.sourceEngine}.accounts`)
const connectTargetLabel = ref(`${props.targetEngine}.clients`)

const previewKind = ref<'mongodb' | 'postgresql'>('mongodb')
const previewEntityName = ref('Entity preview')
const previewMongoSample = ref<Record<string, any> | null>(null)
const previewTableColumns = ref<string[]>([])
const previewTableRows = ref<Array<Record<string, any>>>([])
const previewEntity = ref<DatabaseEntity | null>(null)
const previewLoading = ref(false)
const previewError = ref('')
const previewRequestToken = ref(0)
const selectedMappingTitle = ref(`${props.sourceEngine}.accounts -> ${props.targetEngine}.clients`)
const mappingValidationText = ref('')

const draftName = ref('MongoDB accounts to PostgreSQL clients')
const draftDescription = ref('Visual migration flow from source_db to target_db')

const isDryRunRunning = ref(false)
const showFailedRecords = ref(false)
const failedRecords = ref([
  'rec_011 -> createdAt invalid date',
  'rec_024 -> required field state missing',
  'rec_037 -> DBRef company unresolved',
  'rec_041 -> createdAt invalid date',
  'rec_072 -> zip_code invalid format',
  'rec_099 -> createdAt invalid date',
])

const createTableForm = ref<CreateTableForm>({
  tableName: 'customers',
  schema: 'public',
  creationMode: 'Empty table',
  sourceEntity: 'accounts',
  primaryKey: 'id',
})

const normalizeEngine = (engine: string): 'mongodb' | 'postgresql' => {
  return engine.toLowerCase().includes('postgre') ? 'postgresql' : 'mongodb'
}

const countFields = (value: unknown): number => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return 0
  }

  return Object.keys(value as Record<string, any>).length
}

const toEntityId = (prefix: 'src' | 'tgt', name: string) => {
  const normalized = name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase()
  return `${prefix}-${normalized}`
}

const buildEntitiesFromConnection = (
  names: string[],
  prefix: 'src' | 'tgt',
  engineName: string,
  sample: Record<string, any> | null,
  sampleCount: number,
): DatabaseEntity[] => {
  const engine = normalizeEngine(engineName)
  const kind = engine === 'postgresql' ? 'table' : 'collection'
  const metadata = engine === 'postgresql'
    ? ['table', 'schema', 'constraints', 'indexes']
    : ['collection', 'objectId', 'arrays', 'DBRef']

  const fieldsCount = Math.max(countFields(sample), 1)
  const recordsLabel = sample ? `${Math.max(sampleCount, 1)} sample records` : '-- records'

  return names.map((name) => ({
    id: toEntityId(prefix, name),
    name,
    engine,
    kind,
    recordsLabel,
    fieldsCount,
    metadata,
    details: engine === 'postgresql'
      ? ['Schema loaded', 'Constraints pending', 'Indexes pending']
      : ['Nested: --', 'Arrays: --', 'DBRefs: --'],
  }))
}

const syncEntitiesFromConnection = () => {
  const sourceNames = props.sourceEntityNames || []
  const targetNames = props.targetEntityNames || []
  const sourceSample = props.sourceSamples?.[0] || null
  const targetSample = props.targetSamples?.[0] || null

  const sourceFromConnection = buildEntitiesFromConnection(
    sourceNames,
    'src',
    props.sourceEngine,
    sourceSample,
    props.sourceSamples.length,
  )

  const targetFromConnection = buildEntitiesFromConnection(
    targetNames,
    'tgt',
    props.targetEngine,
    targetSample,
    props.targetSamples.length,
  )

  const customTargets = targetEntityList.value.filter((item) => item.id.startsWith('custom-tgt-'))
  sourceEntityList.value = sourceFromConnection
  targetEntityList.value = [...customTargets, ...targetFromConnection]

  if (createTableForm.value.sourceEntity === 'accounts' && sourceFromConnection.length > 0) {
    createTableForm.value.sourceEntity = sourceFromConnection[0].name
  }
}

watch(
  () => [props.sourceEntityNames, props.targetEntityNames, props.sourceSamples, props.targetSamples, props.sourceEngine, props.targetEngine],
  syncEntitiesFromConnection,
  { immediate: true, deep: true },
)

const toastVisible = ref(false)
const toastMessage = ref('')
let toastTimeout: number | undefined

const showToast = (message: string) => {
  toastMessage.value = message
  toastVisible.value = true
  if (toastTimeout) {
    window.clearTimeout(toastTimeout)
  }
  toastTimeout = window.setTimeout(() => {
    toastVisible.value = false
  }, 2200)
}

const saveDraft = () => {
  isSaveDraftModalOpen.value = false
  showToast('Draft saved successfully.')
}

const openDryRun = () => {
  isDryRunDrawerOpen.value = true
  runDryTestAgain()
}

const runDryTestAgain = () => {
  showFailedRecords.value = false
  isDryRunRunning.value = true
  window.setTimeout(() => {
    isDryRunRunning.value = false
  }, 900)
}

const continueToReview = () => {
  isDryRunDrawerOpen.value = false
  isReviewViewOpen.value = true
}

const adjustMappingFromDryRun = () => {
  isDryRunDrawerOpen.value = false
  isConfigureMappingDrawerOpen.value = true
  isConfigureMappingDrawerCollapsed.value = false
  showToast('Configure mapping opened.')
}

const updateCreateTableField = (field: keyof CreateTableForm, value: string) => {
  createTableForm.value = {
    ...createTableForm.value,
    [field]: value,
  }
}

const createTargetTable = () => {
  targetEntityList.value.unshift({
    id: `custom-tgt-${createTableForm.value.tableName.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase()}`,
    name: createTableForm.value.tableName,
    engine: 'postgresql',
    kind: 'table',
    recordsLabel: '0 rows',
    fieldsCount: 1,
    metadata: ['table', 'schema', 'constraints', 'indexes'],
    details: ['0 required', '0 constraints', '0 indexes'],
  })
  isCreateTargetTableModalOpen.value = false
  showToast('Target table created successfully.')
}

const enableSelectMode = () => {
  activeMode.value = 'select'
  selectedNodeForConnect.value = null
  pendingTargetNode.value = null
  showToast('Select mode enabled. Click a node to inspect details.')
}

const enableConnectMode = () => {
  activeMode.value = 'connect'
  selectedNodeId.value = null
  selectedNodeForConnect.value = null
  pendingTargetNode.value = null
  showToast('Connect mode enabled. Select a source node and then a target node.')
}

const onNodeSelected = (node: CanvasNode) => {
  if (activeMode.value === 'select') {
    selectedNodeId.value = node.id
    const entity = allEntities.value.find((item) => item.id === node.entityId)
    showToast(`Selected node: ${entity?.name || node.entityId}`)
    return
  }

  const isSource = node.entityId.startsWith('src-')
  const isTarget = node.entityId.startsWith('tgt-')

  if (!selectedNodeForConnect.value) {
    if (!isSource) {
      showToast('Select a source node first.')
      return
    }
    selectedNodeForConnect.value = node
    showToast('Source selected. Now select a target node.')
    return
  }

  if (!isTarget) {
    showToast('Select a target node to complete connection.')
    return
  }

  const sourceEntity = allEntities.value.find((item) => item.id === selectedNodeForConnect.value?.entityId)
  const targetEntity = allEntities.value.find((item) => item.id === node.entityId)
  pendingTargetNode.value = node
  connectSourceLabel.value = `${props.sourceEngine}.${sourceEntity?.name || 'accounts'}`
  connectTargetLabel.value = `${props.targetEngine}.${targetEntity?.name || 'clients'}`
  isCreateMappingModalOpen.value = true
}

const confirmCreateMapping = () => {
  if (selectedNodeForConnect.value && pendingTargetNode.value) {
    const sourceId = selectedNodeForConnect.value.id
    const targetId = pendingTargetNode.value.id
    const sourceEntity = allEntities.value.find((item) => item.id === selectedNodeForConnect.value?.entityId)
    const targetEntity = allEntities.value.find((item) => item.id === pendingTargetNode.value?.entityId)
    const label = `${sourceEntity?.name || 'source'} -> ${targetEntity?.name || 'target'}`
    const alreadyExists = canvasConnectionList.value.some(
      (conn) => conn.sourceNodeId === sourceId && conn.targetNodeId === targetId,
    )

    if (!alreadyExists) {
      canvasConnectionList.value.push({
        id: `conn-${sourceId}-${targetId}-${Date.now()}`,
        sourceNodeId: sourceId,
        targetNodeId: targetId,
        label,
        status: 'needs_review',
        mappedFields: 8,
        totalFields: targetEntity?.fieldsCount ?? 14,
        subtitle: 'Needs review',
      })
      selectedMappingTitle.value = `${props.sourceEngine}.${sourceEntity?.name || 'accounts'} -> ${props.targetEngine}.${targetEntity?.name || 'clients'}`
      showToast('Source connected to target successfully.')
    } else {
      showToast('This source and target are already connected.')
    }
  }

  isCreateMappingModalOpen.value = false
  isConfigureMappingDrawerOpen.value = true
  isConfigureMappingDrawerCollapsed.value = false
  selectedNodeForConnect.value = null
  pendingTargetNode.value = null
}

const applyAutoLayout = () => {
  const useAlternate = canvasNodeList.value.some((node) => node.x < 100)
  canvasNodeList.value = canvasNodeList.value.map((node, index) => ({
    ...node,
    x: useAlternate ? 90 + (index % 2) * 360 : 40 + (index % 2) * 428,
    y: 52 + Math.floor(index / 2) * 216,
  }))
  showToast('Canvas layout updated.')
}

const clearCanvas = () => {
  canvasNodeList.value = []
  canvasConnectionList.value = []
  isClearCanvasModalOpen.value = false
  isConfigureMappingDrawerOpen.value = false
  selectedNodeId.value = null
  selectedNodeForConnect.value = null
  pendingTargetNode.value = null
  showToast('Canvas cleared.')
}

const zoomIn = () => {
  canvasZoom.value = Math.min(160, canvasZoom.value + 10)
}

const zoomOut = () => {
  canvasZoom.value = Math.max(60, canvasZoom.value - 10)
}

const resetZoom = () => {
  canvasZoom.value = 100
}

const fitView = () => {
  if (canvasNodeList.value.length === 0) {
    canvasZoom.value = 100
    return
  }
  canvasZoom.value = 90
}

const defaultPositionForEntity = (entityId: string): { x: number; y: number } => {
  const isSource = entityId.startsWith('src-')
  const sameSideCount = canvasNodeList.value.filter((node) => node.entityId.startsWith(isSource ? 'src-' : 'tgt-')).length
  const baseX = isSource ? 80 : 700
  const xOffset = (sameSideCount % 2) * 30
  const y = 80 + Math.floor(sameSideCount / 2) * 180
  return { x: baseX + xOffset, y }
}

const addEntityToCanvas = (entityId: string) => {
  const position = defaultPositionForEntity(entityId)
  onDropEntity({
    entityId,
    x: position.x,
    y: position.y,
  })
}

const onMoveNode = (payload: { nodeId: string; x: number; y: number }) => {
  const node = canvasNodeList.value.find((item) => item.id === payload.nodeId)
  if (!node) {
    return
  }
  node.x = payload.x
  node.y = payload.y
}

const onDropEntity = (payload: { entityId: string; x: number; y: number }) => {
  const entity = allEntities.value.find((item) => item.id === payload.entityId)
  if (!entity) {
    return
  }

  const existingNode = canvasNodeList.value.find((node) => node.entityId === payload.entityId)
  if (existingNode) {
    existingNode.x = payload.x
    existingNode.y = payload.y
    selectedNodeId.value = existingNode.id
    showToast(`${entity.name} moved on canvas.`)
    return
  }

  const newNodeId = `node-${entity.id}-${Date.now()}`
  canvasNodeList.value.push({
    id: newNodeId,
    entityId: entity.id,
    x: payload.x,
    y: payload.y,
    status: 'not_connected',
  })
  selectedNodeId.value = newNodeId
  showToast(`${entity.name} added to canvas.`)
}

const normalizeSampleItems = (responseData: any): Record<string, any>[] => {
  return responseData?.items || responseData?.samples || []
}

const getFallbackSampleForEntity = (entity: DatabaseEntity): Record<string, any> | null => {
  const isSourceEntity = entity.id.startsWith('src-')
  const list = isSourceEntity ? props.sourceSamples : props.targetSamples
  return list[0] || null
}

const resolveConnectionForEntity = (entity: DatabaseEntity) => {
  return entity.id.startsWith('src-') ? props.sourceConnection : props.targetConnection
}

const loadMongoPreviewForEntity = async (entity: DatabaseEntity) => {
  const token = ++previewRequestToken.value
  previewLoading.value = true
  previewError.value = ''

  const connection = resolveConnectionForEntity(entity)
  const connectionString = connection?.connectionString || ''
  const database = connection?.database || ''

  if (!connectionString || !database) {
    previewMongoSample.value = getFallbackSampleForEntity(entity)
    previewError.value = 'Connection string or database is missing for preview.'
    previewLoading.value = false
    return
  }

  try {
    const response = await apiClient.loadMongoSamples({
      connectionString,
      database,
      collection: entity.name,
      authEnabled: Boolean(connection?.authEnabled),
      username: connection?.username || '',
      password: connection?.password || '',
      authSource: connection?.authSource || '',
      limit: 1,
    })

    if (token !== previewRequestToken.value) {
      return
    }

    const items = normalizeSampleItems(response.data)
    previewMongoSample.value = items[0] || null

    if (!items.length) {
      previewError.value = 'No documents found in this collection for preview.'
    }
  } catch (error: any) {
    if (token !== previewRequestToken.value) {
      return
    }
    previewMongoSample.value = getFallbackSampleForEntity(entity)
    previewError.value = error?.response?.data?.detail || error?.message || 'Failed to load preview data.'
  } finally {
    if (token === previewRequestToken.value) {
      previewLoading.value = false
    }
  }
}

const openPreview = async (entity: DatabaseEntity) => {
  previewEntity.value = entity
  previewEntityName.value = `${entity.engine === 'mongodb' ? props.sourceEngine : props.targetEngine}.${entity.name}`
  previewError.value = ''
  previewLoading.value = false
  previewMongoSample.value = null
  previewTableColumns.value = []
  previewTableRows.value = []

  isDataPreviewDrawerOpen.value = true

  const isSourceEntity = entity.id.startsWith('src-')
  const sample = isSourceEntity ? (props.sourceSamples[0] || null) : (props.targetSamples[0] || null)

  previewKind.value = entity.engine === 'mongodb' ? 'mongodb' : 'postgresql'

  if (previewKind.value === 'mongodb') {
    await loadMongoPreviewForEntity(entity)
    return
  }

  if (previewKind.value === 'postgresql') {
    const rawColumns = sample && typeof sample === 'object'
      ? Object.keys(sample).slice(0, 6)
      : []
    previewTableColumns.value = rawColumns.length > 0
      ? rawColumns
      : ['id', 'name', 'document', 'email', 'city', 'state']
    previewTableRows.value = sample && typeof sample === 'object'
      ? [sample]
      : []
  } else {
    previewTableColumns.value = []
    previewTableRows.value = []
  }
}

const openMapFields = (entity: DatabaseEntity) => {
  const isSourceEntity = entity.id.startsWith('src-')
  const sourceName = isSourceEntity
    ? entity.name
    : (sourceEntityList.value[0]?.name || 'source')
  const targetName = isSourceEntity
    ? (targetEntityList.value[0]?.name || 'target')
    : entity.name

  selectedMappingTitle.value = `${props.sourceEngine}.${sourceName} -> ${props.targetEngine}.${targetName}`
  isConfigureMappingDrawerOpen.value = true
  isConfigureMappingDrawerCollapsed.value = false
}

const openMapFieldsFromPreview = () => {
  if (previewEntity.value) {
    openMapFields(previewEntity.value)
  }
  isDataPreviewDrawerOpen.value = false
}

const useAsTarget = () => {
  isSchemaDetailsDrawerOpen.value = false
  showToast('Target table selected for mapping.')
}

const adjustMappingFromValidation = () => {
  isFlowValidationDrawerOpen.value = false
  isConfigureMappingDrawerOpen.value = true
  isConfigureMappingDrawerCollapsed.value = false
  showToast('Configure mapping opened.')
}

const validateMapping = () => {
  mappingValidationText.value = [
    'Mapping validation completed.',
    '1 warning found.',
    '',
    'Validation Result',
    '',
    '12 fields mapped',
    'No incompatible types found',
    'company.$id requires DBRef reference collection',
    '2 optional fields are unmapped',
  ].join('\n')
  showToast('Mapping validation completed. 1 warning found.')
}

const saveMapping = () => {
  const hasWarning = fieldMappingRows.value.some((row) => row.status === 'warning')
  showToast(hasWarning ? 'Mapping saved with warnings.' : 'Mapping saved successfully.')
}

const createMigrationJob = () => {
  isCreateJobConfirmOpen.value = false
  showToast('Migration job created successfully.')
}
</script>

<style scoped>
.visual-builder-view {
  display: grid;
  gap: 12px;
  min-height: calc(100vh - 170px);
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr) minmax(280px, 340px);
  gap: 12px;
  min-height: 0;
}

.main-grid.no-source {
  grid-template-columns: minmax(0, 1fr) minmax(280px, 340px);
}

.canvas-column {
  min-width: 0;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 10px;
}

.canvas-column-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.panel-toggle {
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #d6e5f6;
  font-size: 12px;
  font-weight: 600;
  padding: 7px 10px;
}

.right-rail {
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 0;
}

.route-path {
  margin: 0;
  color: #67e8f9;
  font-size: 12px;
  font-weight: 600;
}

.inline-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(2, 6, 23, 0.7);
  display: grid;
  place-items: center;
  padding: 20px;
}

.inline-modal-card {
  width: min(500px, 100%);
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  padding: 16px;
  display: grid;
  gap: 12px;
}

.inline-modal-card h3,
.inline-modal-card p {
  margin: 0;
}

.inline-modal-card h3 {
  color: #f8fafc;
}

.inline-modal-card p {
  color: #d2e2f5;
  font-size: 13px;
}

.inline-modal-card footer {
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
  color: #d3e5f8;
}

.btn-primary {
  border: 1px solid rgba(34, 197, 94, 0.45);
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%);
  color: #04210f;
}

@media (max-width: 1700px) {
  .main-grid {
    grid-template-columns: minmax(260px, 320px) minmax(0, 1fr) minmax(260px, 320px);
  }
}

@media (max-width: 1280px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .main-grid.no-source {
    grid-template-columns: 1fr;
  }
}
</style>
