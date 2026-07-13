/**
 * Configuração centralizada de API
 */
import axios, { AxiosInstance } from 'axios'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/',
      timeout: 30000,
    })
  }

  // Exploration endpoints
  async validateMongoConnection(payload: any) {
    return this.client.post('/api/explore/validate', payload)
  }

  async validatePostgresConnection(payload: any) {
    return this.client.post('/api/explore/postgres/validate', payload)
  }

  async loadPostgresDatabases(payload: any) {
    return this.client.post('/api/explore/postgres/databases', payload)
  }

  async loadPostgresSchemas(payload: any) {
    return this.client.post('/api/explore/postgres/schemas', payload)
  }

  async loadPostgresTables(payload: any) {
    return this.client.post('/api/explore/postgres/tables', payload)
  }

  async loadMongoDatabases(payload: any) {
    return this.client.post('/api/explore/databases', payload)
  }

  async loadMongoCollections(payload: any) {
    return this.client.post('/api/explore/collections', payload)
  }

  async loadMongoSamples(payload: any) {
    return this.client.post('/api/explore/sample', payload)
  }

  // Migration endpoints
  async previewMigration(payload: any) {
    return this.client.post('/api/migrate/preview', payload)
  }

  async createMigrationJob(payload: any) {
    return this.client.post('/api/jobs/insert', payload)
  }

  async executeMigration(payload: any) {
    return this.client.post('/api/migration/execute', payload)
  }

  // Jobs endpoints
  async getJobs() {
    return this.client.get('/api/jobs/')
  }

  async getJobById(jobId: string) {
    return this.client.get(`/api/jobs/${jobId}`)
  }

  async rerunJob(jobId: string) {
    return this.client.post(`/api/jobs/${jobId}/rerun`, {})
  }

  async deleteJob(jobId: string) {
    return this.client.delete(`/api/jobs/${jobId}`)
  }

  // Templates endpoints
  async getTemplates() {
    return this.client.get('/api/templates/')
  }

  async createTemplate(payload: any) {
    return this.client.post('/api/templates/', payload)
  }

  async deleteTemplate(templateId: string) {
    return this.client.delete(`/api/templates/${templateId}`)
  }

  async applyTemplate(templateId: string) {
    return this.client.get(`/api/templates/${templateId}`)
  }

  // Keycloak endpoints
  async validateKeycloakConnection(payload: any) {
    return this.client.post('/api/keycloak/validate', payload)
  }

  async listKeycloakUsers(payload: any) {
    return this.client.post('/api/keycloak/users', payload)
  }

  async previewKeycloakMigration(payload: any) {
    return this.client.post('/api/keycloak/preview', payload)
  }

  async executeKeycloakMigration(payload: any) {
    return this.client.post('/api/keycloak/execute', payload)
  }
}

export const apiClient = new ApiClient()
