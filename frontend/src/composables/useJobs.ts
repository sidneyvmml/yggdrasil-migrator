/**
 * Composable para gerenciar jobs
 * Responsabilidade: polling, paginação, sorting, CRUD de jobs
 */
import { ref, computed, onBeforeUnmount } from 'vue'
import { apiClient } from '@/services/api'
import { JobItem, JobsUIState } from '@/types/migration'
import { SortBy } from '@/types/ui'

export function useJobs() {
  const jobs = ref<JobItem[]>([])
  const uiState = ref<JobsUIState>({
    currentPage: 1,
    pageSize: 10,
    totalPages: 1,
    sortBy: 'date_desc',
    loading: false,
    rerunLoadingId: '',
    deleteLoadingId: '',
  })

  let jobsPollTimer: ReturnType<typeof setInterval> | null = null

  /**
   * Ordena jobs por data
   */
  const jobsSorted = computed(() => {
    const sorted = [...jobs.value]
    if (uiState.value.sortBy === 'date_asc') {
      sorted.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
    } else {
      sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    }
    return sorted
  })

  /**
   * Aplica paginação aos jobs
   */
  const jobsPaginated = computed(() => {
    const start = (uiState.value.currentPage - 1) * uiState.value.pageSize
    const end = start + uiState.value.pageSize
    return jobsSorted.value.slice(start, end)
  })

  /**
   * Calcula total de páginas
   */
  const jobsTotalPages = computed(() =>
    Math.ceil(jobsSorted.value.length / uiState.value.pageSize)
  )

  /**
   * Carrega jobs do servidor
   */
  const loadJobs = async (force: boolean = false): Promise<void> => {
    if (!force && uiState.value.loading) return

    uiState.value.loading = true
    try {
      const response = await apiClient.getJobs()
      if (Array.isArray(response.data)) {
        jobs.value = response.data
      } else if (Array.isArray(response.data?.jobs)) {
        jobs.value = response.data.jobs
      } else {
        jobs.value = []
      }
      uiState.value.currentPage = 1 // Reset paginação ao recarregar
    } catch (error) {
      console.error('Erro ao carregar jobs:', error)
      jobs.value = []
    } finally {
      uiState.value.loading = false
    }
  }

  /**
   * Inicia polling de jobs
   */
  const startJobsPolling = (intervalMs: number = 3000): void => {
    if (jobsPollTimer) return

    // Load once immediately so Jobs screen is populated without waiting for interval.
    loadJobs(true)

    jobsPollTimer = setInterval(() => {
      loadJobs()
    }, intervalMs)
  }

  /**
   * Para polling de jobs
   */
  const stopJobsPolling = (): void => {
    if (jobsPollTimer) {
      clearInterval(jobsPollTimer)
      jobsPollTimer = null
    }
  }

  /**
   * Reexecuta um job
   */
  const rerunJob = async (jobId: string): Promise<void> => {
    uiState.value.rerunLoadingId = jobId
    try {
      await apiClient.rerunJob(jobId)
      await loadJobs(true)
    } catch (error) {
      console.error('Erro ao reexecutar job:', error)
    } finally {
      uiState.value.rerunLoadingId = ''
    }
  }

  /**
   * Deleta um job
   */
  const deleteJob = async (jobId: string): Promise<void> => {
    uiState.value.deleteLoadingId = jobId
    try {
      await apiClient.deleteJob(jobId)
      await loadJobs(true)
    } catch (error) {
      console.error('Erro ao deletar job:', error)
    } finally {
      uiState.value.deleteLoadingId = ''
    }
  }

  /**
   * Muda página de paginação
   */
  const setPage = (page: number): void => {
    const maxPage = jobsTotalPages.value || 1
    uiState.value.currentPage = Math.max(1, Math.min(page, maxPage))
  }

  /**
   * Muda quantidade de itens por página
   */
  const setPageSize = (size: number): void => {
    uiState.value.pageSize = size
    uiState.value.currentPage = 1
  }

  /**
   * Muda ordenação
   */
  const setSortBy = (sortBy: SortBy): void => {
    uiState.value.sortBy = sortBy
    uiState.value.currentPage = 1
  }

  /**
   * Cleanup ao desmontar
   */
  onBeforeUnmount(() => {
    stopJobsPolling()
  })

  return {
    jobs,
    uiState,
    jobsSorted,
    jobsPaginated,
    jobsTotalPages,
    loadJobs,
    startJobsPolling,
    stopJobsPolling,
    rerunJob,
    deleteJob,
    setPage,
    setPageSize,
    setSortBy,
  }
}
