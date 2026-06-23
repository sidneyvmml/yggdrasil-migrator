/**
 * Composable para gerenciar lógica de migration
 * Responsabilidade: preview, campo mapping, execução de jobs
 */
import { ref, reactive } from 'vue'
import { apiClient } from '@/services/api'
import { MappingRow, PreviewSample } from '@/types/migration'
import { MongoConnectionConfig, KeycloakConnectionConfig } from '@/types/engine'

export function useMigration() {
  const mappingRows = ref<MappingRow[]>([])
  const previewRows = ref<PreviewSample[]>([])
  const sourceDocumentForMapping = ref<any>(null)
  const sourceSamplesLoading = ref(false)
  const previewLoading = ref(false)
  const createJobLoading = ref(false)
  const keycloakUsernameSourceField = ref('username')

  /**
   * Sincroniza mappings automáticos a partir de samples
   */
  const syncMappingsFromSamples = (): void => {
    if (!sourceDocumentForMapping.value) return

    const fields = Object.keys(sourceDocumentForMapping.value)
    const newMappings: MappingRow[] = fields
      .filter((field) => field !== '_id')
      .map((field) => ({
        sourceField: field,
        targetField: field,
        transformation: '',
      }))

    mappingRows.value = newMappings
  }

  /**
   * Carrega samples Keycloak
   */
  const loadKeycloakUsers = async (
    connection: KeycloakConnectionConfig,
    limit: number = 10
  ): Promise<PreviewSample[]> => {
    sourceSamplesLoading.value = true
    try {
      const payload = {
        baseUrl: connection.baseUrl.trim(),
        realm: connection.realm.trim(),
        authMode: connection.authMode,
        clientId: connection.clientId.trim(),
        clientSecret:
          connection.authMode === 'client_credentials' ? connection.clientSecret : null,
        username: connection.authMode === 'password' ? connection.username.trim() : null,
        password: connection.authMode === 'password' ? connection.password : null,
        limit,
      }

      const response = await apiClient.listKeycloakUsers(payload)
      const items = response.data.items || []

      previewRows.value = items
      if (items.length > 0) {
        sourceDocumentForMapping.value = items[0]
        syncMappingsFromSamples()
      }

      return items
    } catch (error) {
      console.error('Erro ao carregar usuários Keycloak:', error)
      return []
    } finally {
      sourceSamplesLoading.value = false
    }
  }

  /**
   * Carrega samples MongoDB
   */
  const loadMongoSamples = async (
    connection: MongoConnectionConfig,
    limit: number = 10
  ): Promise<PreviewSample[]> => {
    sourceSamplesLoading.value = true
    try {
      const response = await apiClient.loadMongoSamples({
        connectionString: connection.connectionString,
        database: connection.database,
        collection: connection.collection,
        authEnabled: connection.authEnabled,
        username: connection.username,
        password: connection.password,
        authSource: connection.authSource,
        limit,
      })

      const items = response.data.samples || []
      previewRows.value = items
      if (items.length > 0) {
        sourceDocumentForMapping.value = items[0]
        syncMappingsFromSamples()
      }

      return items
    } catch (error) {
      console.error('Erro ao carregar samples MongoDB:', error)
      return []
    } finally {
      sourceSamplesLoading.value = false
    }
  }

  /**
   * Adiciona nova linha de mapping
   */
  const addMappingRow = (): void => {
    mappingRows.value.push({
      sourceField: '',
      targetField: '',
      transformation: '',
    })
  }

  /**
   * Remove linha de mapping
   */
  const removeMappingRow = (index: number): void => {
    mappingRows.value.splice(index, 1)
  }

  /**
   * Atualiza linha de mapping
   */
  const updateMappingRow = (
    index: number,
    field: keyof MappingRow,
    value: string
  ): void => {
    if (index >= 0 && index < mappingRows.value.length) {
      mappingRows.value[index][field] = value
    }
  }

  /**
   * Limpa estado de migration
   */
  const resetMigrationState = (): void => {
    mappingRows.value = []
    previewRows.value = []
    sourceDocumentForMapping.value = null
    keycloakUsernameSourceField.value = 'username'
  }

  return {
    mappingRows,
    previewRows,
    sourceDocumentForMapping,
    sourceSamplesLoading,
    previewLoading,
    createJobLoading,
    keycloakUsernameSourceField,
    syncMappingsFromSamples,
    loadKeycloakUsers,
    loadMongoSamples,
    addMappingRow,
    removeMappingRow,
    updateMappingRow,
    resetMigrationState,
  }
}
