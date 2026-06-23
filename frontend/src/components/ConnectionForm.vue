<template>
  <article class="connection-form">
    <div class="connection-form-header">
      <h3>{{ title }}</h3>
      <span v-if="engine" :class="['engine-badge', engine]">{{ engine }}</span>
    </div>

    <!-- MongoDB Connection Form -->
    <template v-if="engine === 'MongoDB' || engine === 'PostgreSQL'">
      <label>
        Connection String
        <input
          v-model="mongoForm.connectionString"
          type="text"
          placeholder="mongodb://localhost:27017"
          @input="$emit('update-connection', mongoForm)"
        />
      </label>

      <label class="connection-field-label">
        <span class="connection-label-row">
          <span>Enable Authentication</span>
          <button
            type="button"
            :class="['auth-switch', { 'is-on': mongoForm.authEnabled }]"
            aria-label="Enable authentication"
            :aria-pressed="mongoForm.authEnabled"
            @click="mongoForm.authEnabled = !mongoForm.authEnabled; $emit('update-connection', mongoForm)"
          >
            <span class="auth-switch-track"></span>
          </button>
        </span>
      </label>

      <template v-if="mongoForm.authEnabled">
        <label>
          Username
          <input
            v-model="mongoForm.username"
            type="text"
            placeholder="username"
            @input="$emit('update-connection', mongoForm)"
          />
        </label>

        <label>
          Password
          <input
            v-model="mongoForm.password"
            type="password"
            placeholder="password"
            @input="$emit('update-connection', mongoForm)"
          />
        </label>

        <label>
          Auth Source
          <input
            v-model="mongoForm.authSource"
            type="text"
            placeholder="admin"
            @input="$emit('update-connection', mongoForm)"
          />
        </label>
      </template>

      <div class="connection-actions">
        <button class="primary-button" :disabled="testing" @click="$emit('test-connection')">
          {{ testing ? 'Testing...' : 'Test Connection' }}
        </button>
        <button v-if="status === 'success'" class="status-success">✓ Connected</button>
        <button v-else-if="status === 'error'" class="status-error">✗ Failed</button>
      </div>

      <p v-if="message" :class="['connection-message', status]">{{ message }}</p>
    </template>

    <!-- Keycloak Connection Form -->
    <template v-else-if="engine === 'Keycloak'">
      <label>
        Base URL
        <input
          v-model="keycloakForm.baseUrl"
          type="text"
          placeholder="https://keycloak.example.com"
          @input="$emit('update-connection', keycloakForm)"
        />
      </label>

      <label>
        Realm
        <input
          v-model="keycloakForm.realm"
          type="text"
          placeholder="master"
          @input="$emit('update-connection', keycloakForm)"
        />
      </label>

      <label>
        Auth Mode
        <select v-model="keycloakForm.authMode" @change="$emit('update-connection', keycloakForm)">
          <option value="client_credentials">Client Credentials</option>
          <option value="password">Username e Senha</option>
        </select>
      </label>

      <label>
        Client ID
        <input
          v-model="keycloakForm.clientId"
          type="text"
          placeholder="admin-cli"
          @input="$emit('update-connection', keycloakForm)"
        />
      </label>

      <template v-if="keycloakForm.authMode === 'client_credentials'">
        <label>
          Client Secret
          <input
            v-model="keycloakForm.clientSecret"
            type="password"
            placeholder="client_secret"
            @input="$emit('update-connection', keycloakForm)"
          />
        </label>
      </template>

      <template v-else>
        <label>
          Username
          <input
            v-model="keycloakForm.username"
            type="text"
            placeholder="admin"
            @input="$emit('update-connection', keycloakForm)"
          />
        </label>

        <label>
          Password
          <input
            v-model="keycloakForm.password"
            type="password"
            placeholder="password"
            @input="$emit('update-connection', keycloakForm)"
          />
        </label>
      </template>

      <div class="connection-actions">
        <button class="primary-button" :disabled="testing" @click="$emit('test-connection')">
          {{ testing ? 'Testing...' : 'Test Connection' }}
        </button>
        <button v-if="connected" class="status-success">✓ Connected</button>
        <button v-else-if="status === 'error'" class="status-error">✗ Failed</button>
      </div>

      <p v-if="message" :class="['connection-message', status]">{{ message }}</p>
    </template>
  </article>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { EngineType, MongoConnectionConfig, KeycloakConnectionConfig } from '@/types'

interface Props {
  title: string
  engine: EngineType | ''
  mongoConnection?: MongoConnectionConfig
  keycloakConnection?: KeycloakConnectionConfig
  testing?: boolean
  status?: 'success' | 'error' | ''
  message?: string
  connected?: boolean
}

interface Emits {
  'update-connection': [connection: MongoConnectionConfig | KeycloakConnectionConfig]
  'test-connection': []
}

const props = withDefaults(defineProps<Props>(), {
  testing: false,
  status: '',
  message: '',
  connected: false,
})

defineEmits<Emits>()

// Mongo form state - pode vir de props ou inicializar vazio
const mongoForm = reactive<MongoConnectionConfig>({
  connectionString: props.mongoConnection?.connectionString || 'mongodb://localhost:27017',
  database: props.mongoConnection?.database || '',
  collection: props.mongoConnection?.collection || '',
  authEnabled: props.mongoConnection?.authEnabled || false,
  username: props.mongoConnection?.username || '',
  password: props.mongoConnection?.password || '',
  authSource: props.mongoConnection?.authSource || '',
})

// Keycloak form state
const keycloakForm = reactive<KeycloakConnectionConfig>({
  baseUrl: props.keycloakConnection?.baseUrl || '',
  realm: props.keycloakConnection?.realm || '',
  authMode: props.keycloakConnection?.authMode || 'client_credentials',
  clientId: props.keycloakConnection?.clientId || '',
  clientSecret: props.keycloakConnection?.clientSecret || '',
  username: props.keycloakConnection?.username || '',
  password: props.keycloakConnection?.password || '',
})
</script>

<style scoped>
.connection-form {
  display: grid;
  gap: 12px;
  padding: 16px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
}

.connection-form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.connection-form-header h3 {
  margin: 0;
}

.engine-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: capitalize;
}

.connection-field-label {
  display: block;
}

.connection-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.auth-switch {
  border: 0;
  background: transparent;
  padding: 0;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.auth-switch-track {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  border-radius: 999px;
  background: #d1d5db;
  border: 2px solid #8b8f97;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.auth-switch-track::after {
  content: '';
  position: absolute;
  top: 1px;
  left: 1px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f8fafc;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.45);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.auth-switch.is-on .auth-switch-track {
  background: #35d063;
  border-color: #35d063;
}

.auth-switch.is-on .auth-switch-track::after {
  transform: translateX(22px);
}

.auth-switch:focus-visible .auth-switch-track {
  box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.35);
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: #cbd5e1;
  font-weight: 500;
}

label input[type='checkbox'] {
  width: auto;
  cursor: pointer;
}

input[type='text'],
input[type='password'],
select {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #cbd5e1;
  font-size: 0.9rem;
  font-family: 'Courier New', monospace;
}

input[type='text']:focus,
input[type='password']:focus,
select:focus {
  outline: none;
  border-color: #475569;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.connection-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.primary-button {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #22c55e;
  border-radius: 8px;
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-button:hover:not(:disabled) {
  background: rgba(34, 197, 94, 0.2);
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-success,
.status-error {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: default;
}

.status-success {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-error {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.connection-message {
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  margin: 0;
}

.connection-message.success {
  background: rgba(16, 185, 129, 0.1);
  color: #86efac;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.connection-message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
</style>
