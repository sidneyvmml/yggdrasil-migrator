/**
 * Composable para gerenciar estado de conexão
 * Responsabilidade: validação, estado de conexão, limpeza
 */
import { reactive, ref } from 'vue'
import { apiClient } from '@/services/api'
import { MongoConnectionConfig, KeycloakConnectionConfig, ConnectionStatus } from '@/types/engine'

export interface ConnectionState {
  mongoSource: MongoConnectionConfig & ConnectionStatus
  mongoTarget: MongoConnectionConfig & ConnectionStatus
  keycloakSource: KeycloakConnectionConfig & ConnectionStatus
  keycloakTarget: KeycloakConnectionConfig & ConnectionStatus
}

export function useConnection() {
  const mongoConnectionSource = reactive<MongoConnectionConfig & ConnectionStatus>({
    connectionString: 'mongodb://localhost:27017',
    database: '',
    collection: '',
    authEnabled: false,
    username: '',
    password: '',
    authSource: '',
    status: '',
    message: '',
    testing: false,
  })

  const mongoConnectionTarget = reactive<MongoConnectionConfig & ConnectionStatus>({
    connectionString: 'mongodb://localhost:27017',
    database: '',
    collection: '',
    authEnabled: false,
    username: '',
    password: '',
    authSource: '',
    status: '',
    message: '',
    testing: false,
  })

  const keycloakConnectionSource = reactive<KeycloakConnectionConfig & ConnectionStatus>({
    baseUrl: '',
    realm: '',
    authMode: 'client_credentials',
    clientId: '',
    clientSecret: '',
    username: '',
    password: '',
    status: '',
    message: '',
    testing: false,
    connected: false,
  })

  const keycloakConnectionTarget = reactive<KeycloakConnectionConfig & ConnectionStatus>({
    baseUrl: '',
    realm: '',
    authMode: 'client_credentials',
    clientId: '',
    clientSecret: '',
    username: '',
    password: '',
    status: '',
    message: '',
    testing: false,
    connected: false,
  })

  /**
   * Valida conexão MongoDB
   */
  const testMongoConnection = async (
    connection: MongoConnectionConfig & ConnectionStatus,
    isTarget: boolean = false
  ): Promise<void> => {
    connection.testing = true
    connection.status = ''
    connection.message = ''

    try {
      const response = await apiClient.validateMongoConnection({
        connectionString: connection.connectionString,
        authEnabled: connection.authEnabled,
        username: connection.username,
        password: connection.password,
        authSource: connection.authSource,
      })

      if (response.data.connected) {
        connection.status = 'success'
        connection.message = 'Conexão válida com o MongoDB.'
      } else {
        connection.status = 'error'
        connection.message = 'Falha ao validar a conexão.'
      }
    } catch (error: any) {
      connection.status = 'error'
      connection.message =
        error.response?.data?.detail || error.message || 'Erro na conexão.'
    } finally {
      connection.testing = false
    }
  }

  /**
   * Valida conexão Keycloak
   */
  const testKeycloakConnection = async (
    connection: KeycloakConnectionConfig & ConnectionStatus
  ): Promise<void> => {
    connection.testing = true
    connection.message = ''

    try {
      const payload = {
        baseUrl: connection.baseUrl.trim(),
        realm: connection.realm.trim(),
        authMode: connection.authMode,
        clientId: connection.clientId.trim(),
        clientSecret:
          connection.authMode === 'client_credentials'
            ? connection.clientSecret
            : null,
        username: connection.authMode === 'password' ? connection.username.trim() : null,
        password: connection.authMode === 'password' ? connection.password : null,
      }

      const response = await apiClient.validateKeycloakConnection(payload)

      if (response.data.connected) {
        connection.connected = true
        connection.message = 'Conexao valida com o Keycloak.'
      } else {
        connection.connected = false
        connection.message = 'Falha ao validar conexao com Keycloak.'
      }
    } catch (error: any) {
      connection.connected = false
      connection.message =
        error.response?.data?.detail || error.message || 'Falha ao validar conexao com Keycloak.'
    } finally {
      connection.testing = false
    }
  }

  /**
   * Carrega databases MongoDB
   */
  const loadMongoDatabases = async (connection: MongoConnectionConfig) => {
    try {
      const response = await apiClient.loadMongoDatabases({
        connectionString: connection.connectionString,
        authEnabled: connection.authEnabled,
        username: connection.username,
        password: connection.password,
        authSource: connection.authSource,
      })
      return response.data.databases || []
    } catch (error) {
      console.error('Erro ao carregar databases:', error)
      return []
    }
  }

  /**
   * Carrega collections MongoDB
   */
  const loadMongoCollections = async (connection: MongoConnectionConfig) => {
    try {
      const response = await apiClient.loadMongoCollections({
        connectionString: connection.connectionString,
        database: connection.database,
        authEnabled: connection.authEnabled,
        username: connection.username,
        password: connection.password,
        authSource: connection.authSource,
      })
      return response.data.collections || []
    } catch (error) {
      console.error('Erro ao carregar collections:', error)
      return []
    }
  }

  /**
   * Limpa estado de conexão
   */
  const resetConnectionState = () => {
    mongoConnectionSource.status = ''
    mongoConnectionSource.message = ''
    mongoConnectionSource.database = ''
    mongoConnectionSource.collection = ''

    mongoConnectionTarget.status = ''
    mongoConnectionTarget.message = ''
    mongoConnectionTarget.database = ''
    mongoConnectionTarget.collection = ''

    keycloakConnectionSource.connected = false
    keycloakConnectionSource.message = ''

    keycloakConnectionTarget.connected = false
    keycloakConnectionTarget.message = ''
  }

  return {
    mongoConnectionSource,
    mongoConnectionTarget,
    keycloakConnectionSource,
    keycloakConnectionTarget,
    testMongoConnection,
    testKeycloakConnection,
    loadMongoDatabases,
    loadMongoCollections,
    resetConnectionState,
  }
}
