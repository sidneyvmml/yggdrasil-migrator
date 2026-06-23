<template>
  <article class="jobs-list-container">
    <div class="jobs-header">
      <h2>Migration Jobs</h2>
      <div class="jobs-controls">
        <select v-model="sortBy" class="form-select" @change="$emit('sort-changed', sortBy)">
          <option value="date_desc">Mais recentes primeiro</option>
          <option value="date_asc">Mais antigos primeiro</option>
        </select>
        <button class="primary-button secondary" :disabled="loading" @click="$emit('refresh')">
          {{ loading ? 'Recarregando...' : 'Recarregar agora' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="card">
      <p>Carregando jobs...</p>
    </div>

    <div v-else-if="paginatedJobs.length === 0" class="card">
      <p>Nenhum job criado ainda.</p>
    </div>

    <div v-else class="jobs-grid">
      <article v-for="job in paginatedJobs" :key="job.jobId" class="card job-card">
        <div class="job-header">
          <h3>Job #{{ job.jobId }}</h3>
          <div class="job-header-actions">
            <span :class="['job-status', normalizeJobStatus(job.status)]">
              {{ statusLabel(job.status) }}
            </span>
            <button
              class="wizard-secondary job-rerun-button"
              :disabled="!job.canRerun || rerunLoadingId === job.jobId"
              @click="$emit('job-rerun', job.jobId)"
            >
              {{ rerunLoadingId === job.jobId ? 'Re-running...' : 'Re-run' }}
            </button>
            <button
              class="wizard-secondary job-delete-button"
              :disabled="deleteLoadingId === job.jobId"
              @click="$emit('job-delete', job.jobId)"
            >
              {{ deleteLoadingId === job.jobId ? 'Removing...' : 'Remove' }}
            </button>
          </div>
        </div>

        <div class="job-progress-track">
          <div class="job-progress-fill" :style="{ width: `${job.progress || 0}%` }"></div>
        </div>
        <p class="job-progress-text">{{ job.progress || 0 }}%</p>

        <div class="job-steps">
          <div
            v-for="stage in JOB_STAGES"
            :key="`${job.jobId}-${stage}`"
            :class="['job-step', stageState(job, stage)]"
          >
            <span class="job-step-label">{{ stageLabel(stage) }}</span>
            <span v-if="stageState(job, stage) === 'active'" class="job-spinner"></span>
            <span v-else-if="stageState(job, stage) === 'done'" class="job-step-done">ok</span>
          </div>
        </div>

        <div v-if="job.result" class="job-result">
          <p>
            Processados: {{ job.result.processed ?? 0 }} |
            Inseridos: {{ job.result.inserted ?? 0 }} |
            Mesclados: {{ job.result.merged ?? 0 }} |
            Ignorados: {{ job.result.skipped ?? 0 }}
          </p>
          <p v-if="jobNoOutputHint(job)" class="job-hint warning">{{ jobNoOutputHint(job) }}</p>
          <p v-if="job.result.error" class="job-error">{{ job.result.error }}</p>
        </div>

        <div class="job-footer">
          <small>Criado em {{ formatJobDate(job.createdAt) }}</small>
          <button class="wizard-secondary" @click="$emit('job-details', job.jobId)">
            Ver detalhes
          </button>
        </div>
      </article>
    </div>

    <!-- Pagination Controls -->
    <div v-if="jobs.length > 0" class="jobs-pagination">
      <div class="pagination-info">
        <span
          >Mostrando {{ (currentPage - 1) * pageSize + 1 }} até
          {{ Math.min(currentPage * pageSize, sortedJobs.length) }} de {{ sortedJobs.length }}
          jobs</span
        >
      </div>
      <div class="pagination-controls">
        <label>
          Itens por página:
          <select v-model.number="pageSize" class="form-select" @change="$emit('page-size-changed', pageSize)">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </label>
        <div class="pagination-buttons">
          <button
            @click="$emit('page-changed', Math.max(1, currentPage - 1))"
            :disabled="currentPage === 1"
            class="pagination-button"
          >
            ← Anterior
          </button>
          <span class="pagination-text">Página {{ currentPage }} de {{ totalPages }}</span>
          <button
            @click="$emit('page-changed', Math.min(totalPages, currentPage + 1))"
            :disabled="currentPage === totalPages"
            class="pagination-button"
          >
            Próximo →
          </button>
        </div>
      </div>
    </div>

    <div class="jobs-footer">
      <button class="wizard-secondary" @click="$emit('back')">
        ← Voltar
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { JobItem, SortBy } from '@/types'

interface Props {
  jobs: JobItem[]
  loading?: boolean
  currentPage?: number
  pageSize?: number
  sortBy?: SortBy
  rerunLoadingId?: string
  deleteLoadingId?: string
}

interface Emits {
  'refresh': []
  'job-rerun': [jobId: string]
  'job-delete': [jobId: string]
  'job-details': [jobId: string]
  'page-changed': [page: number]
  'page-size-changed': [size: number]
  'sort-changed': [sort: SortBy]
  'back': []
}

const JOB_STAGES = ['pending', 'loading_source', 'mapping_fields', 'inserting_documents', 'done']

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  currentPage: 1,
  pageSize: 10,
  sortBy: 'date_desc',
  rerunLoadingId: '',
  deleteLoadingId: '',
})

defineEmits<Emits>()

const currentPage = ref(props.currentPage)
const pageSize = ref(props.pageSize)
const sortBy = ref(props.sortBy)

/**
 * Ordena jobs por data
 */
const sortedJobs = computed(() => {
  const sorted = [...props.jobs]
  if (sortBy.value === 'date_asc') {
    sorted.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
  } else {
    sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  }
  return sorted
})

/**
 * Aplica paginação
 */
const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedJobs.value.slice(start, end)
})

/**
 * Total de páginas
 */
const totalPages = computed(() => Math.ceil(sortedJobs.value.length / pageSize.value))

/**
 * Normaliza status do job
 */
const normalizeJobStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'pending',
    loading_source: 'pending',
    mapping_fields: 'pending',
    inserting_documents: 'pending',
    done: 'done',
    failed: 'failed',
  }
  return statusMap[status] || 'pending'
}

/**
 * Rótulo legível para status
 */
const statusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: 'Pendente',
    loading_source: 'Carregando...',
    mapping_fields: 'Mapeando...',
    inserting_documents: 'Inserindo...',
    done: 'Concluído',
    failed: 'Falhou',
  }
  return labels[status] || 'Desconhecido'
}

/**
 * Estado atual de um stage
 */
const stageState = (job: JobItem, stage: string): 'done' | 'active' | 'pending' => {
  const stageIndex = JOB_STAGES.indexOf(stage)
  const currentIndex = JOB_STAGES.indexOf(job.status)

  if (stageIndex < currentIndex) return 'done'
  if (stageIndex === currentIndex && job.status !== 'done') return 'active'
  return 'pending'
}

/**
 * Rótulo para stage
 */
const stageLabel = (stage: string): string => {
  const labels: Record<string, string> = {
    pending: 'Aguardando',
    loading_source: 'Carregando',
    mapping_fields: 'Mapeando',
    inserting_documents: 'Inserindo',
    done: 'Finalizado',
  }
  return labels[stage] || stage
}

/**
 * Dica se não houve output
 */
const jobNoOutputHint = (job: JobItem): string => {
  if (!job.result) return ''
  const total = (job.result.inserted ?? 0) + (job.result.merged ?? 0) + (job.result.skipped ?? 0)
  if (total === 0) {
    return 'Verifique se a query/filtro retorna dados'
  }
  return ''
}

/**
 * Formata data do job
 */
const formatJobDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.jobs-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.jobs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.jobs-header h2 {
  margin: 0;
}

.jobs-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.jobs-controls .form-select {
  padding: 8px 10px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #111827;
  color: #cbd5e1;
}

.jobs-grid {
  display: grid;
  gap: 12px;
}

.job-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
}

.job-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.job-header h3 {
  margin: 0;
  font-size: 1rem;
}

.job-header-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.job-status {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.job-status.pending {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
}

.job-status.done {
  background: rgba(16, 185, 129, 0.15);
  color: #047857;
}

.job-status.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #b91c1c;
}

.job-rerun-button,
.job-delete-button {
  margin-top: 0;
  padding: 7px 10px;
  font-size: 0.8rem;
}

.job-progress-track {
  height: 8px;
  border-radius: 999px;
  background: #334155;
  overflow: hidden;
}

.job-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #10b981);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.job-progress-text {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

.job-steps {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
}

.job-step {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.85rem;
  background: #0f172a;
  border: 1px solid #334155;
}

.job-step.done {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.job-step.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: #06b6d4;
}

.job-step-label {
  flex: 1;
  color: #cbd5e1;
}

.job-step-done {
  font-size: 0.75rem;
  color: #047857;
  font-weight: 700;
  text-transform: uppercase;
}

.job-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #93c5fd;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin-job 0.8s linear infinite;
}

@keyframes spin-job {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.job-result {
  padding: 10px;
  background: #0f172a;
  border-radius: 8px;
  border-left: 3px solid #22c55e;
}

.job-result p {
  margin: 0;
  font-size: 0.84rem;
  color: #cbd5e1;
}

.job-error {
  color: #b91c1c !important;
}

.job-hint.warning {
  color: #92400e !important;
  font-weight: 600;
}

.job-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #334155;
}

.job-footer small {
  color: #94a3b8;
}

.jobs-pagination {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #334155;
  display: grid;
  gap: 14px;
}

.pagination-info {
  font-size: 0.84rem;
  color: #94a3b8;
}

.pagination-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.pagination-controls label {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.84rem;
  color: #cbd5e1;
}

.pagination-controls .form-select {
  padding: 6px 8px;
  border: 1px solid #334155;
  border-radius: 6px;
  background: #111827;
  color: #cbd5e1;
}

.pagination-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-button {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 6px;
  background: #111827;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 0.84rem;
  transition: all 0.2s ease;
}

.pagination-button:hover:not(:disabled) {
  background: #1f2937;
  border-color: #475569;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 0.84rem;
  color: #94a3b8;
  min-width: 120px;
  text-align: center;
}

.jobs-footer {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #334155;
}

.card {
  padding: 14px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
}

.card p {
  margin: 0;
  color: #cbd5e1;
}

.primary-button.secondary {
  border: 1px solid #334155;
  background: #111827;
  color: #cbd5e1;
}

.primary-button.secondary:hover:not(:disabled) {
  background: #1f2937;
  border-color: #475569;
}

.wizard-secondary {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #111827;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.wizard-secondary:hover:not(:disabled) {
  background: #1f2937;
  border-color: #475569;
}

.wizard-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
