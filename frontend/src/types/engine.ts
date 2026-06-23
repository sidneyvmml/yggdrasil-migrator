/**
 * Tipos e interfaces para engines de migração
 */

export type EngineType = 'MongoDB' | 'PostgreSQL' | 'MySQL' | 'Oracle' | 'Keycloak' | 'Redis'
export type AuthMode = 'client_credentials' | 'password'

export interface Engine {
  name: EngineType
  type: string
  description: string
  features: string[]
  available: boolean
  selectable: boolean
}

/**
 * Configurações de conexão genéricas
 */
export interface MongoConnectionConfig {
  connectionString: string
  database: string
  collection: string
  authEnabled: boolean
  username: string
  password: string
  authSource: string
}

export interface PostgresConnectionConfig {
  host: string
  port: string
  database: string
  username: string
  password: string
}

export interface KeycloakConnectionConfig {
  baseUrl: string
  realm: string
  authMode: AuthMode
  clientId: string
  clientSecret: string | null
  username: string | null
  password: string | null
}

export type ConnectionConfig = MongoConnectionConfig | PostgresConnectionConfig | KeycloakConnectionConfig

export interface ConnectionStatus {
  status: '' | 'success' | 'error'
  message: string
  testing: boolean
  connected?: boolean
}

export interface ValidationResult {
  connected: boolean
  message?: string
}
