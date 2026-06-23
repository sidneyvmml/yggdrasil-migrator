<template>
  <div id="app">
    <div class="global-shell">
      <!-- Sidebar -->
      <aside class="global-sidebar">
        <div class="global-logo">
          <img class="global-logo-image" :src="appLogoUrl" alt="Yggdrasil logo" />
          <div>
            <strong>YGGDRASIL</strong>
            <small>MIGRATOR</small>
          </div>
        </div>
        <nav class="global-nav">
          <button
            :class="['global-nav-item', { active: ui.activeTab.value === 'dashboard' }]"
            @click="ui.setActiveTab('dashboard')"
          >
            Dashboard
          </button>
          <button
            :class="['global-nav-item', { active: ui.isInMigrationFlow() }]"
            @click="ui.setActiveTab('engines')"
          >
            New Migration
          </button>
          <button
            :class="['global-nav-item', { active: ui.activeTab.value === 'connections' }]"
            @click="ui.setActiveTab('connections')"
          >
            Connections
          </button>
          <button
            :class="['global-nav-item', { active: ui.activeTab.value === 'jobs' }]"
            @click="goToJobsFromPreview"
          >
            Migration Jobs
          </button>
          <button
            :class="['global-nav-item', { active: ui.activeTab.value === 'templates' }]"
            @click="ui.setActiveTab('templates')"
          >
            Templates
          </button>
        </nav>
        <div class="global-sidebar-footer">
          <div class="global-env">Environment: Local</div>
          <div class="global-user">Admin User<br />admin@yggdrasil.local</div>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="global-main">
        <!-- Header -->
        <header class="global-main-header">
          <div class="global-topbar-actions global-topbar-actions-standalone">
            <ThemeSwitcher />
            <button class="global-icon-button">?</button>
            <div class="global-avatar">A</div>
          </div>

          <!-- Migration Flow Header with Stepper -->
          <section v-if="ui.isInMigrationFlow()" class="migration-flow-header">
            <div class="migration-flow-copy">
              <h2>New Migration</h2>
              <p>{{ getMigrationStepDescription() }}</p>
            </div>
            <Stepper
              :steps="MIGRATION_FLOW_TABS_FULL"
              :current-step="getCurrentMigrationStep()"
              :allow-backtrack="true"
              @step-selected="ui.goToMigrationStep"
            />
          </section>
        </header>

        <!-- Main Content Area -->
        <main class="content">
          <!-- Dashboard -->
          <section v-if="ui.activeTab.value === 'dashboard'" class="panel">
            <header class="dashboard-topbar">
              <div>
                <h2>Dashboard</h2>
                <p>Monitor migrations, connections and data movement</p>
              </div>
              <button class="wizard-primary" @click="ui.setActiveTab('engines')">New Migration</button>
            </header>

            <!-- Metrics Row -->
            <div class="dashboard-metrics">
              <article class="dashboard-metric-card">
                <p class="dashboard-label">Total Migrations</p>
                <strong>128</strong>
                <span>+12 this week</span>
              </article>
              <article class="dashboard-metric-card">
                <p class="dashboard-label">Running Jobs</p>
                <strong>3</strong>
                <span>2 MongoDB -> PostgreSQL, 1 MongoDB -> MongoDB</span>
              </article>
              <article class="dashboard-metric-card">
                <p class="dashboard-label">Success Rate</p>
                <strong>96.4%</strong>
                <span>last 30 days</span>
              </article>
              <article class="dashboard-metric-card">
                <p class="dashboard-label">Records Migrated</p>
                <strong>2.8M</strong>
                <span>across all jobs</span>
              </article>
              <article class="dashboard-metric-card">
                <p class="dashboard-label">Failed Records</p>
                <strong>432</strong>
                <span>138 need review</span>
              </article>
            </div>

            <!-- Active Migration & Connection Health -->
            <div class="dashboard-middle-grid">
              <article class="dashboard-active-card">
                <div class="dashboard-card-title-row">
                  <h3>Active Migration</h3>
                  <span class="wizard-status optional">Running</span>
                </div>
                <p class="dashboard-flow">MongoDB.accounts -> PostgreSQL.clients</p>
                <div class="dashboard-progress-track">
                  <div class="dashboard-progress-fill" style="width: 73%"></div>
                </div>
                <p class="dashboard-progress-text">73%</p>
                <div class="dashboard-kpi-grid">
                  <div><span>Processed</span><strong>91,008 / 124,392</strong></div>
                  <div><span>Success</span><strong>90,870</strong></div>
                  <div><span>Failed</span><strong>138</strong></div>
                  <div><span>Speed</span><strong>2,300 docs/min</strong></div>
                  <div><span>ETA</span><strong>14 min</strong></div>
                </div>
                <div class="dashboard-actions">
                  <button class="wizard-secondary" @click="ui.setActiveTab('jobs')">View Job</button>
                  <button class="wizard-secondary">Pause</button>
                </div>
              </article>

              <article class="dashboard-health-card">
                <h3>Connection Health</h3>
                <ul class="dashboard-health-list">
                  <li><span class="dot ok"></span>MongoDB Source <em>Healthy, 24ms</em></li>
                  <li><span class="dot ok"></span>PostgreSQL Target <em>Healthy, 38ms</em></li>
                  <li><span class="dot warn"></span>MongoDB Production <em>Warning, last check 12 min ago</em></li>
                  <li><span class="dot err"></span>PostgreSQL Backup <em>Offline, authentication failed</em></li>
                </ul>
              </article>
            </div>

            <!-- Recent Jobs Table -->
            <article class="dashboard-jobs-card">
              <div class="dashboard-card-title-row">
                <h3>Recent Migration Jobs</h3>
                <button class="wizard-secondary" @click="ui.setActiveTab('jobs')">Open Jobs</button>
              </div>
              <div class="dashboard-table-wrap">
                <table class="dashboard-table">
                  <thead>
                    <tr>
                      <th>Job</th>
                      <th>Source</th>
                      <th>Target</th>
                      <th>Status</th>
                      <th>Progress</th>
                      <th>Records</th>
                      <th>Failed</th>
                      <th>Duration</th>
                      <th>Started At</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="job in dashboardRecentJobs" :key="job.job">
                      <td>{{ job.job }}</td>
                      <td>{{ job.source }}</td>
                      <td>{{ job.target }}</td>
                      <td><span :class="['wizard-status', job.statusClass]">{{ job.status }}</span></td>
                      <td>{{ job.progress }}</td>
                      <td>{{ job.records }}</td>
                      <td>{{ job.failed }}</td>
                      <td>{{ job.duration }}</td>
                      <td>{{ job.startedAt }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </article>

            <!-- Issues & Quick Actions -->
            <div class="dashboard-bottom-grid">
              <article class="dashboard-issues-card">
                <h3>Issues Requiring Attention</h3>
                <ul>
                  <li v-for="issue in dashboardIssues" :key="issue">{{ issue }}</li>
                </ul>
              </article>

              <article class="dashboard-actions-card">
                <h3>Quick Actions</h3>
                <div class="dashboard-quick-actions">
                  <button class="wizard-secondary" @click="ui.setActiveTab('engines')">New Migration</button>
                  <button class="wizard-secondary" @click="ui.setActiveTab('connections')">Create Connection</button>
                  <button class="wizard-secondary" @click="ui.setActiveTab('mapping')">Run Dry Test</button>
                  <button class="wizard-secondary" @click="ui.setActiveTab('templates')">Open Templates</button>
                  <button class="wizard-secondary" @click="ui.setActiveTab('jobs')">View Failed Records</button>
                </div>
              </article>
            </div>
          </section>

          <!-- Engine Selection -->
          <section v-else-if="ui.activeTab.value === 'engines'" class="panel">
            <header class="engines-topbar">
              <div class="wizard-topbar-left">
                <button class="wizard-icon-button" @click="ui.setActiveTab('dashboard')">←</button>
                <h2>New Migration</h2>
              </div>
              <div class="wizard-topbar-right">
              </div>
            </header>

            <div class="engines-header">
              <h2>Choose Database Engines</h2>
              <p>Select where your data comes from and where it should go.</p>
            </div>

            <!-- Migration Path Card -->
            <article class="engines-path-card">
              <h3>Migration Path</h3>
              <div class="engines-path-row">
                <div class="engine-selected-card source">
                  <img
                    v-if="getPathEngineImage(engine.selectedSourceEngine.value)"
                    class="engine-path-image"
                    :src="getPathEngineImage(engine.selectedSourceEngine.value)"
                    :alt="`${engine.selectedSourceEngine.value} image`"
                  />
                  <span v-else class="engine-brand-glyph engine-path-glyph">{{ getEngineGlyph(engine.selectedSourceEngine.value) }}</span>
                  <div class="engine-card-text">
                    <span class="engine-role-badge source">Source</span>
                    <h4>{{ engine.selectedSourceEngine.value }}</h4>
                    <p>{{ engine.selectedSourceEngine.value === 'MongoDB' ? 'Document database' : 'Engine selected' }}</p>
                    <small>{{ engine.selectedSourceEngine.value === 'MongoDB' ? 'Collections, documents, arrays and DBRef support.' : 'Selected as source engine.' }}</small>
                  </div>
                </div>
                <div class="engine-path-arrow">→</div>
                <div class="engine-selected-card target">
                  <img
                    v-if="getPathEngineImage(engine.selectedTargetEngine.value)"
                    class="engine-path-image"
                    :src="getPathEngineImage(engine.selectedTargetEngine.value)"
                    :alt="`${engine.selectedTargetEngine.value} image`"
                  />
                  <span v-else class="engine-brand-glyph engine-path-glyph">{{ getEngineGlyph(engine.selectedTargetEngine.value) }}</span>
                  <div class="engine-card-text">
                    <span class="engine-role-badge target">Target</span>
                    <h4>{{ engine.selectedTargetEngine.value }}</h4>
                    <p>{{ engine.selectedTargetEngine.value === 'MongoDB' ? 'Document database' : 'Engine selected' }}</p>
                    <small>{{ engine.selectedTargetEngine.value === 'MongoDB' ? 'Collections, documents, arrays and DBRef support.' : 'Selected as target engine.' }}</small>
                  </div>
                </div>
              </div>

              <div class="engine-compatibility">
                <div class="dashboard-card-title-row">
                  <h4>{{ engine.selectedSourceEngine.value }} → {{ engine.selectedTargetEngine.value }} Compatibility</h4>
                  <span :class="['wizard-status', engine.isCompatible.value ? 'valid' : 'warn']">{{ engine.isCompatible.value ? 'Supported' : 'Not compatible' }}</span>
                </div>
                <ul>
                  <li v-if="engine.selectedSourceEngine.value === 'MongoDB'">✓ ObjectId conversion available</li>
                  <li v-if="engine.selectedSourceEngine.value === 'MongoDB'">✓ Nested object extraction available</li>
                  <li v-if="engine.selectedSourceEngine.value === 'MongoDB' && engine.selectedTargetEngine.value === 'MongoDB'">✓ Array to JSONB transformation supported</li>
                  <li v-if="engine.selectedSourceEngine.value === 'MongoDB'">⚠ DBRef requires manual configuration</li>
                  <li>✓ Target constraints will be validated before execution</li>
                </ul>
              </div>
            </article>

            <!-- Available Engines Grid -->
            <article class="engines-available-card">
              <h3>Available Engines</h3>
              <div class="engines-grid">
                <article
                  v-for="eng in availableEngines"
                  :key="eng.name"
                  :class="[
                    'engine-card',
                    eng.available ? 'available' : 'disabled',
                    engine.selectedSourceEngine.value === eng.name || engine.selectedTargetEngine.value === eng.name ? 'selected' : ''
                  ]"
                >
                  <div class="engine-card-head">
                    <div class="engine-brand-row">
                      <img
                        v-if="getEngineLogo(eng.name)"
                        class="engine-brand-logo"
                        :src="getEngineLogo(eng.name)"
                        :alt="`${eng.name} logo`"
                      />
                      <span v-else class="engine-brand-glyph">{{ getEngineGlyph(eng.name) }}</span>
                      <div class="engine-brand-text">
                        <div class="engine-title-with-badge">
                          <h4>{{ eng.name }}</h4>
                          <span v-if="eng.name === 'Keycloak'" class="engine-badge">Keycloak to Keycloak only</span>
                        </div>
                      </div>
                    </div>
                    <span :class="['wizard-status', eng.available ? 'valid' : 'warn']">{{ eng.available ? 'Available' : 'Coming soon' }}</span>
                  </div>
                  <p>{{ eng.type }}</p>
                  <small>{{ eng.description }}</small>
                  <div class="engine-tags">
                    <span v-for="feature in eng.features" :key="feature">{{ feature }}</span>
                  </div>
                  <div class="engine-actions">
                    <button
                      :class="['wizard-secondary', 'engine-action-button', 'source', { active: engine.selectedSourceEngine.value === eng.name }]"
                      :disabled="!eng.selectable"
                      :aria-pressed="engine.selectedSourceEngine.value === eng.name"
                      @click="engine.setSourceEngine(eng.name)"
                    >
                      Set as Source
                    </button>
                    <button
                      :class="['wizard-secondary', 'engine-action-button', 'target', { active: engine.selectedTargetEngine.value === eng.name }]"
                      :disabled="!eng.selectable"
                      :aria-pressed="engine.selectedTargetEngine.value === eng.name"
                      @click="engine.setTargetEngine(eng.name)"
                    >
                      Set as Target
                    </button>
                  </div>
                </article>
              </div>
            </article>

            <!-- Footer Actions -->
            <footer class="wizard-actions">
              <div>
                <button class="wizard-secondary" @click="ui.setActiveTab('dashboard')">Cancel</button>
              </div>
              <div>
                <button class="wizard-primary" :disabled="!engine.isCompatible.value" @click="ui.nextTab()">Continue</button>
              </div>
            </footer>
          </section>

          <!-- Connection Forms -->
          <section v-else-if="ui.activeTab.value === 'connections'" class="panel">
            <div class="connections-header-row">
              <h2>Connections</h2>
              <div class="migration-mode-control">
                <span class="migration-mode-text">Modo de Migração</span>
                <div class="migration-mode-toggle-row">
                  <span :class="['migration-mode-option', { active: ui.migrationMode.value === 'simple' }]">Simples</span>
                  <button
                    type="button"
                    :class="['auth-switch', 'migration-mode-switch', { 'is-on': ui.migrationMode.value === 'custom' }]"
                    aria-label="Alternar modo de migração"
                    :aria-pressed="ui.migrationMode.value === 'custom'"
                    @click="ui.migrationMode.value = ui.migrationMode.value === 'simple' ? 'custom' : 'simple'"
                  >
                    <span class="auth-switch-track"></span>
                  </button>
                  <span :class="['migration-mode-option', { active: ui.migrationMode.value === 'custom' }]">Personalizada</span>
                </div>
              </div>
            </div>

            <!-- Source & Target Connection Forms -->
            <div class="form-grid">
              <div class="card form-card">
                <h3>Source {{ engine.selectedSourceEngine.value }}</h3>
                <ConnectionForm
                  :title="`Source ${engine.selectedSourceEngine.value}`"
                  :engine="engine.selectedSourceEngine.value"
                  :mongo-connection="connection.mongoConnectionSource"
                  :keycloak-connection="connection.keycloakConnectionSource"
                  :testing="sourceTesting"
                  :status="sourceStatus"
                  :message="sourceMessage"
                  :connected="sourceConnected"
                  @update-connection="updateSourceConnection"
                  @test-connection="testSourceConnection"
                />

                <template v-if="ui.migrationMode.value === 'simple' && engine.selectedSourceEngine.value === 'MongoDB'">
                  <div class="connection-action-row">
                    <button class="wizard-secondary" :disabled="sourceDatabasesLoading || !sourceConnected" @click="loadSourceDatabases">
                      {{ sourceDatabasesLoading ? 'Carregando...' : 'Carregar Bancos de Dados' }}
                    </button>
                    <button class="wizard-secondary" :disabled="sourceCollectionsLoading || !connection.mongoConnectionSource.database || !sourceConnected" @click="loadSourceCollections">
                      {{ sourceCollectionsLoading ? 'Carregando...' : 'Carregar Coleções' }}
                    </button>
                  </div>

                  <label v-if="sourceDatabasesSafe.length" class="connection-field-label">
                    Database
                    <select v-model="connection.mongoConnectionSource.database" class="form-select">
                      <option value="">-- Selecione --</option>
                      <option v-for="db in sourceDatabasesSafe" :key="`source-${db}`" :value="db">{{ db }}</option>
                    </select>
                  </label>

                  <label v-if="sourceCollectionsSafe.length" class="connection-field-label">
                    Collection
                    <select v-model="connection.mongoConnectionSource.collection" class="form-select">
                      <option value="">-- Selecione --</option>
                      <option v-for="col in sourceCollectionsSafe" :key="`source-col-${col}`" :value="col">{{ col }}</option>
                    </select>
                  </label>

                  <button
                    v-if="connection.mongoConnectionSource.collection"
                    class="primary-button"
                    style="margin-top:12px"
                    :disabled="sourceSamplesLoading"
                    @click="viewSourceSample"
                  >
                    {{ sourceSamplesLoading ? 'Carregando...' : 'Visualizar Dados' }}
                  </button>

                  <div v-if="sourceSamples.length" class="samples-list" style="margin-top:12px">
                    <h4>Documentos (primeiros 10)</h4>
                    <label class="preview-merge-toggle" style="margin-top: 8px; margin-bottom: 8px;">
                      <input v-model="useSelectedBaseDocument" type="checkbox" />
                      Usar documento-base para mapear campos (opcional)
                    </label>
                    <div class="samples-container">
                      <div v-for="(item, idx) in sourceSamples" :key="idx" class="sample-item">
                        <label v-if="useSelectedBaseDocument && getDocumentId(item)" class="wizard-rule-mode-toggle-label" style="margin-bottom: 8px;">
                          <input
                            type="radio"
                            name="source-base-document"
                            :checked="selectedSourceBaseDocumentId === getDocumentId(item)"
                            @change="selectSourceBaseDocument(item)"
                          />
                          <span>Documento base #{{ idx + 1 }}</span>
                        </label>
                        <pre>{{ JSON.stringify(item, null, 2) }}</pre>
                      </div>
                    </div>
                  </div>
                </template>
              </div>

              <div class="card form-card">
                <h3>Destination {{ engine.selectedTargetEngine.value }}</h3>
                <ConnectionForm
                  :title="`Target ${engine.selectedTargetEngine.value}`"
                  :engine="engine.selectedTargetEngine.value"
                  :mongo-connection="connection.mongoConnectionTarget"
                  :keycloak-connection="connection.keycloakConnectionTarget"
                  :testing="targetTesting"
                  :status="targetStatus"
                  :message="targetMessage"
                  :connected="targetConnected"
                  @update-connection="updateTargetConnection"
                  @test-connection="testTargetConnection"
                />

                <template v-if="ui.migrationMode.value === 'simple' && engine.selectedTargetEngine.value === 'MongoDB'">
                  <div class="connection-action-row">
                    <button class="wizard-secondary" :disabled="targetDatabasesLoading || !targetConnected" @click="loadTargetDatabases">
                      {{ targetDatabasesLoading ? 'Carregando...' : 'Carregar Bancos de Dados' }}
                    </button>
                    <button class="wizard-secondary" :disabled="targetCollectionsLoading || !connection.mongoConnectionTarget.database || !targetConnected" @click="loadTargetCollections">
                      {{ targetCollectionsLoading ? 'Carregando...' : 'Carregar Coleções' }}
                    </button>
                  </div>

                  <label v-if="targetDatabasesSafe.length" class="connection-field-label">
                    Database
                    <select v-model="connection.mongoConnectionTarget.database" class="form-select">
                      <option value="">-- Selecione --</option>
                      <option v-for="db in targetDatabasesSafe" :key="`target-${db}`" :value="db">{{ db }}</option>
                    </select>
                  </label>

                  <label v-if="targetCollectionsSafe.length" class="connection-field-label">
                    Collection
                    <select v-model="connection.mongoConnectionTarget.collection" class="form-select">
                      <option value="">-- Selecione --</option>
                      <option v-for="col in targetCollectionsSafe" :key="`target-col-${col}`" :value="col">{{ col }}</option>
                    </select>
                  </label>

                  <button
                    v-if="connection.mongoConnectionTarget.collection"
                    class="primary-button"
                    style="margin-top:12px"
                    :disabled="destinationSamplesLoading"
                    @click="viewDestinationSample"
                  >
                    {{ destinationSamplesLoading ? 'Carregando...' : 'Visualizar Dados' }}
                  </button>

                  <div v-if="destinationSamples.length" class="samples-list" style="margin-top:12px">
                    <h4>Documentos (primeiros 10)</h4>
                    <div class="samples-container">
                      <div v-for="(item, idx) in destinationSamples" :key="idx" class="sample-item">
                        <pre>{{ JSON.stringify(item, null, 2) }}</pre>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Stage Navigation -->
            <div class="stage-nav" style="margin-top: 16px">
              <button class="wizard-secondary" @click="ui.previousTab()" style="margin-right: auto">Back</button>
                <button class="wizard-primary" :disabled="!sourceConnected || !targetConnected || mappingNavigationLoading" @click="goToMappingFromConnections">
                  {{ mappingNavigationLoading ? 'Carregando...' : 'Mapear dados' }}
                </button>
            </div>
            <p v-if="!sourceConnected || !targetConnected" class="connections-next-hint">
              Selecione os bancos Source e Target para avancar para a proxima etapa.
            </p>
          </section>

          <section v-else-if="ui.activeTab.value === 'mapping'" class="panel wizard-panel">
            <div class="wizard-shell">
              <div class="wizard-main">
                <div class="wizard-header">
                  <div>
                    <h1>Field Mapping &amp; Transformation</h1>
                    <p>Define how data from the source will be mapped and transformed to the target.</p>
                    <div v-if="engine.selectedSourceEngine.value === 'Keycloak' && engine.selectedTargetEngine.value === 'Keycloak'" style="margin-top: 10px; max-width: 360px;">
                      <label>
                        Campo de origem para username no destino
                        <select v-model="migration.keycloakUsernameSourceField.value" class="form-select" style="margin-top: 6px;">
                          <option v-for="field in sourceFieldPaths" :key="`kc-username-${field}`" :value="field">{{ field }}</option>
                        </select>
                      </label>
                    </div>
                  </div>
                  <div class="wizard-connections">
                    <div class="wizard-conn-card">
                      <small>Source</small>
                      <div class="wizard-conn-card-header">
                        <img
                          v-if="getPathEngineImage(engine.selectedSourceEngine.value)"
                          class="wizard-conn-logo"
                          :src="getPathEngineImage(engine.selectedSourceEngine.value)"
                          :alt="`${engine.selectedSourceEngine.value} logo`"
                        />
                        <span v-else class="engine-brand-glyph wizard-conn-glyph">{{ getEngineGlyph(engine.selectedSourceEngine.value) }}</span>
                        <strong>{{ engine.selectedSourceEngine.value }}</strong>
                      </div>
                      <span>{{ connection.mongoConnectionSource.database || 'source_db' }}.{{ connection.mongoConnectionSource.collection || 'accounts' }}</span>
                    </div>
                    <span class="wizard-conn-arrow">&rarr;</span>
                    <div class="wizard-conn-card target">
                      <small>Target</small>
                      <div class="wizard-conn-card-header">
                        <img
                          v-if="getPathEngineImage(engine.selectedTargetEngine.value)"
                          class="wizard-conn-logo"
                          :src="getPathEngineImage(engine.selectedTargetEngine.value)"
                          :alt="`${engine.selectedTargetEngine.value} logo`"
                        />
                        <span v-else class="engine-brand-glyph wizard-conn-glyph">{{ getEngineGlyph(engine.selectedTargetEngine.value) }}</span>
                        <strong>{{ engine.selectedTargetEngine.value }}</strong>
                      </div>
                      <span>{{ connection.mongoConnectionTarget.database || 'target_db' }}.{{ connection.mongoConnectionTarget.collection || 'clients' }}</span>
                    </div>
                  </div>
                </div>

                <div class="wizard-upper-grid">
                  <article class="wizard-card source-panel">
                    <header>
                      <h3>Source Fields</h3>
                      <input class="wizard-search" placeholder="Search source fields..." />
                    </header>
                    <div class="wizard-field-list">
                      <div v-for="field in sourceFieldTree" :key="field.path" class="wizard-field-row" :style="{ paddingLeft: `${field.depth * 14 + 8}px` }">
                        <span class="wizard-field-name">{{ field.path }}</span>
                        <span :class="['wizard-type-pill', field.typeClass]">{{ field.type }}</span>
                      </div>
                    </div>
                    <button class="wizard-secondary" @click="viewSourceSample">Refresh Fields</button>
                  </article>

                  <article class="wizard-card mapping-table-panel">
                    <header class="wizard-table-header">
                      <h3>Mapping Rules ({{ mappingTableRows.length }})</h3>
                      <div>
                        <button class="wizard-secondary" @click="syncMappingsFromSamples">Auto Map</button>
                        <button class="wizard-secondary" @click="openAddRuleModal">Add Rule</button>
                      </div>
                    </header>
                    <div class="wizard-table-wrap">
                      <table class="wizard-table">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Source Field</th>
                            <th>Target Field</th>
                            <th>Type</th>
                            <th>Transform</th>
                            <th>Required</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="row in mappingTableRows" :key="row.model.id">
                            <td>{{ row.index }}</td>
                            <td>
                              <template v-if="row.model.ruleType === 'concat'">
                                <span class="wizard-inline-code">{{ row.model.concatLeftField }} + {{ row.model.concatRightField }}</span>
                              </template>
                              <template v-else-if="row.model.noSource">
                                <span class="wizard-inline-code">Nao existe no source</span>
                              </template>
                              <select
                                v-else
                                :value="row.model.sourceField"
                                class="wizard-select"
                                @change="setDirectRuleSourceField(row.model, ($event.target as HTMLSelectElement).value)"
                              >
                                <option v-for="field in sourceFieldPaths" :key="field" :value="field">{{ field }}</option>
                              </select>
                            </td>
                            <td>
                              <input v-model="row.model.targetField" class="wizard-select" placeholder="target field" />
                            </td>
                            <td>{{ row.typeLabel }}</td>
                            <td>{{ row.transform }}</td>
                            <td>{{ row.required ? 'required' : 'optional' }}</td>
                            <td><span :class="['wizard-status', row.statusClass]">{{ row.status }}</span></td>
                            <td>
                              <div class="wizard-row-actions">
                                <button class="wizard-action-icon" :disabled="row.isFirst" @click="moveMappingRule(row.index - 1, -1)" title="Mover para cima">↑</button>
                                <button class="wizard-action-icon" :disabled="row.isLast" @click="moveMappingRule(row.index - 1, 1)" title="Mover para baixo">↓</button>
                                <button class="wizard-action-icon" @click="openDefaultValueModal(row.model)" title="Set default value">🧷</button>
                                <button class="wizard-action-icon" @click="openDbRefModal(row.model)" title="Configure DBRef">🔗</button>
                                <button class="wizard-remove-button" @click="removeRule(row.model)" title="Excluir campo">🗑</button>
                              </div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </article>

                  <article class="wizard-card target-panel">
                    <header>
                      <h3>Target Fields</h3>
                      <input class="wizard-search" placeholder="Search target fields..." />
                    </header>
                    <div class="wizard-field-list">
                      <div v-for="field in targetFieldList" :key="field.path" class="wizard-field-row">
                        <span class="wizard-field-name">{{ field.path }}</span>
                        <span :class="['wizard-type-pill', field.typeClass]">{{ field.type }}</span>
                      </div>
                    </div>
                  </article>
                </div>

                <div class="wizard-lower-grid">
                  <article class="wizard-card code-panel">
                    <h3>Source Document (Sample)</h3>
                    <pre class="wizard-code"><code><span v-for="(line, idx) in sourceCodeLines" :key="`src-${idx}`"><span class="ln">{{ idx + 1 }}</span>{{ line }}
</span></code></pre>
                  </article>
                  <article class="wizard-card code-panel">
                    <h3>Transformed Output (Sample)</h3>
                    <pre class="wizard-code"><code><span v-for="(line, idx) in mappedCodeLines" :key="`map-${idx}`"><span class="ln">{{ idx + 1 }}</span>{{ line }}
</span></code></pre>
                  </article>
                  <article class="wizard-card validation-panel">
                    <h3>Mapping Validation</h3>
                    <ul class="wizard-checklist">
                      <li>✓ {{ mappedRequiredCount }} required fields mapped</li>
                      <li>✓ {{ optionalUnmappedCount }} optional fields unmapped</li>
                      <li v-if="hasDbRefWarning">⚠ 1 DBRef field needs resolution</li>
                      <li v-if="hasDbRefWarning">⚠ Company reference collection not selected</li>
                      <li v-if="hasDefaultValueWarning">⚠ 1 default value is enabled but empty</li>
                      <li>✓ No incompatible types found</li>
                      <li>✓ Ready to run</li>
                    </ul>
                  </article>
                </div>

                <footer class="wizard-actions">
                  <div>
                    <button class="wizard-secondary" @click="ui.setActiveTab('connections')">Back</button>
                    <button class="wizard-secondary" @click="ui.setActiveTab('templates')">Save as Template</button>
                  </div>
                  <div>
                    <button class="wizard-secondary" @click="mapData">Validate Mapping</button>
                    <button class="wizard-primary" @click="ui.setActiveTab('preview')">Continue</button>
                  </div>
                </footer>

                <div v-if="showAddRuleModal" class="wizard-modal-backdrop" @click.self="closeAddRuleModal">
                  <div class="wizard-modal">
                    <h3>Add Rule</h3>
                    <p>Create a new target field from source data, concatenation, or as a fixed-value field with no source reference.</p>

                    <label class="wizard-modal-label">Rule Type</label>
                    <div class="wizard-rule-mode-toggle">
                      <label><input type="radio" value="new" v-model="addRuleMode" /> New field from existing source</label>
                      <label><input type="radio" value="concat" v-model="addRuleMode" /> Concatenate two source fields</label>
                    </div>

                    <template v-if="addRuleMode === 'new'">
                      <label class="wizard-rule-mode-toggle-label">
                        <input type="checkbox" v-model="addRuleNoSource" />
                        <span>Nao existe no source (campo novo)</span>
                      </label>

                      <template v-if="addRuleNoSource">
                        <label class="wizard-modal-label">Valor padrao (obrigatorio)</label>
                        <input v-model="addRuleNoSourceDefaultRaw" class="wizard-select" placeholder="ex: ativo | 10 | true | JSON" />
                        <p class="connections-next-hint">Esse campo sera enviado como manualMapping, sem referencia no source.</p>
                      </template>

                      <template v-else>
                      <label class="wizard-modal-label">Source field</label>
                      <select v-model="addRuleSourceField" class="wizard-select">
                        <option v-for="field in sourceFieldPaths" :key="`new-${field}`" :value="field">{{ field }}</option>
                      </select>
                      </template>
                    </template>

                    <template v-else>
                      <label class="wizard-modal-label">Concat field 1</label>
                      <select v-model="addRuleConcatLeft" class="wizard-select">
                        <option v-for="field in sourceFieldPaths" :key="`left-${field}`" :value="field">{{ field }}</option>
                      </select>

                      <label class="wizard-modal-label">Concat field 2</label>
                      <select v-model="addRuleConcatRight" class="wizard-select">
                        <option v-for="field in sourceFieldPaths" :key="`right-${field}`" :value="field">{{ field }}</option>
                      </select>

                      <label class="wizard-modal-label">Separator</label>
                      <input v-model="addRuleConcatSeparator" class="wizard-select" placeholder=" " />
                    </template>

                    <label class="wizard-modal-label">Target field name</label>
                    <input v-model="addRuleTargetField" class="wizard-select" placeholder="ex: full_name" />

                    <p v-if="addRuleError" class="wizard-modal-error">{{ addRuleError }}</p>

                    <div class="wizard-modal-actions">
                      <button class="wizard-secondary" @click="closeAddRuleModal">Cancel</button>
                      <button class="wizard-primary" @click="submitAddRule">Add</button>
                    </div>
                  </div>
                </div>

                <div v-if="showDbRefModal" class="wizard-modal-backdrop" @click.self="closeDbRefModal">
                  <div class="wizard-modal">
                    <h3>Configure DBRef</h3>
                    <p>Use this rule to reference an ID from another collection.</p>

                    <label class="wizard-modal-label">Enable DBRef for this rule</label>
                    <label class="wizard-rule-mode-toggle-label">
                      <input type="checkbox" v-model="dbRefEnabledDraft" />
                      <span>Enable DBRef reference</span>
                    </label>

                    <label class="wizard-modal-label">Target field</label>
                    <input class="wizard-select" :value="dbRefEditingRule?.targetField || ''" disabled />

                    <label class="wizard-modal-label">Reference collection</label>
                    <input v-model="dbRefCollectionDraft" class="wizard-select" placeholder="ex: companies" :disabled="!dbRefEnabledDraft" />

                    <label class="wizard-modal-label">Reference field</label>
                    <input v-model="dbRefForeignFieldDraft" class="wizard-select" placeholder="_id" :disabled="!dbRefEnabledDraft" />

                    <p v-if="dbRefError" class="wizard-modal-error">{{ dbRefError }}</p>

                    <div class="wizard-modal-actions">
                      <button class="wizard-secondary" @click="closeDbRefModal">Cancel</button>
                      <button class="wizard-primary" @click="saveDbRefRule">Save</button>
                    </div>
                  </div>
                </div>

                <div v-if="showDefaultValueModal" class="wizard-modal-backdrop" @click.self="closeDefaultValueModal">
                  <div class="wizard-modal">
                    <h3>Default Value</h3>
                    <p>Set a fixed value to be applied to this target field in all migrated records.</p>

                    <label class="wizard-modal-label">Enable default value for this rule</label>
                    <label class="wizard-rule-mode-toggle-label">
                      <input type="checkbox" v-model="defaultValueEnabledDraft" />
                      <span>Enable fixed value</span>
                    </label>

                    <label class="wizard-modal-label">Target field</label>
                    <input class="wizard-select" :value="defaultValueEditingRule?.targetField || ''" disabled />

                    <label class="wizard-modal-label">Default value (raw text)</label>
                    <input
                      v-model="defaultValueRawDraft"
                      class="wizard-select"
                      :disabled="!defaultValueEnabledDraft"
                      placeholder="ex: active | 10 | true | JSON object"
                    />

                    <p v-if="defaultValueError" class="wizard-modal-error">{{ defaultValueError }}</p>

                    <div class="wizard-modal-actions">
                      <button class="wizard-secondary" @click="closeDefaultValueModal">Cancel</button>
                      <button class="wizard-primary" @click="saveDefaultValueRule">Save</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section v-else-if="ui.activeTab.value === 'preview'" class="panel preview-panel">
            <div class="preview-header preview-header-enterprise">
              <div>
                <h2>Review &amp; Job</h2>
                <p>Visão lado a lado do documento de origem e do resultado após o mapeamento.</p>
              </div>
              <div class="wizard-connections">
                <div class="wizard-conn-card">
                  <small>Source</small>
                  <strong>{{ engine.selectedSourceEngine.value }}</strong>
                  <span>{{ connection.mongoConnectionSource.database || 'source_db' }}.{{ connection.mongoConnectionSource.collection || 'accounts' }}</span>
                </div>
                <span class="wizard-conn-arrow">&rarr;</span>
                <div class="wizard-conn-card target">
                  <small>Target</small>
                  <strong>{{ engine.selectedTargetEngine.value }}</strong>
                  <span>{{ connection.mongoConnectionTarget.database || 'target_db' }}.{{ connection.mongoConnectionTarget.collection || 'clients' }}</span>
                </div>
              </div>
            </div>

            <div class="preview-stage">
              <div class="preview-flow">
                <article class="preview-card source">
                  <div class="preview-card-badge">Origem</div>
                  <h3>Collection 1</h3>
                  <div class="preview-field-list">
                    <div v-for="field in previewSourceFields" :key="field.path" class="preview-field-row source-row">
                      <span class="preview-field-name">{{ field.path }}</span>
                      <span class="preview-field-value">{{ field.value }}</span>
                    </div>
                  </div>
                </article>

                <article class="preview-card target">
                  <div class="preview-card-badge success">Destino após mapeamento</div>
                  <h3>Collection 2</h3>
                  <div class="preview-field-list">
                    <div
                      v-for="field in previewMappedFields"
                      :key="field.path"
                      :class="['preview-field-row', field.mode === 'manual' ? 'manual-row' : 'mapped-row']"
                    >
                      <div class="preview-field-meta">
                        <span class="preview-field-name">{{ field.path }}</span>
                        <span :class="['preview-field-tag', field.mode === 'manual' ? 'manual' : 'mapped']">
                          {{ field.mode === 'manual' ? 'Manual' : 'Equivalente' }}
                        </span>
                      </div>
                      <span class="preview-field-value">{{ field.value }}</span>
                    </div>
                  </div>
                </article>
              </div>

              <div class="wizard-card preview-actions">
                <h3>{{ engine.selectedTargetEngine.value === 'Keycloak' ? 'Migrar para o Keycloak de destino' : 'Inserir no Mongo de destino' }}</h3>
                <p>{{ engine.selectedTargetEngine.value === 'Keycloak' ? 'Use o mapeamento atual para migrar 1 ou todos os usuários da origem.' : 'Use o mapeamento atual para inserir 1 ou todos os documentos da origem.' }}</p>
                <p class="preview-warning-text">
                  O preview mostra uma amostra. Ao escolher "Inserir todos", cada documento da collection de origem será processado separadamente.
                </p>
                <div class="preview-actions-row">
                  <label>
                    Quantidade
                    <select v-model="insertMode" class="form-select">
                      <option value="one">Inserir 1 documento</option>
                      <option value="all">Inserir todos os documentos</option>
                    </select>
                  </label>
                  <label v-if="hasStarredsArray" class="preview-merge-toggle">
                    <input v-model="extractStarredsEnabled" type="checkbox" />
                    Extrair somente starreds.starred = true (Favorites)
                  </label>
                  <label class="preview-merge-toggle">
                    <input v-model="mergeDocumentsEnabled" type="checkbox" />
                    Mesclar documentos por chave
                  </label>
                  <label v-if="mergeDocumentsEnabled">
                    Campo de mesclagem
                    <select v-model="mergeByField" class="form-select">
                      <option value="">-- Selecione --</option>
                      <option v-for="field in mergeFieldOptions" :key="field" :value="field">{{ field }}</option>
                    </select>
                  </label>
                  <button class="wizard-primary" @click="createInsertJob" :disabled="createJobLoading || !mappingRows.length">
                    {{ createJobLoading ? 'Criando job...' : 'Inserir no destino' }}
                  </button>
                </div>
                <div v-if="createJobError" class="status-chip error">{{ createJobError }}</div>
                <div class="wizard-actions preview-footer-actions">
                  <div>
                    <button class="wizard-secondary" @click="ui.setActiveTab('mapping')">Voltar ao mapeamento</button>
                  </div>
                  <div>
                    <button class="wizard-secondary" @click="jobs.loadJobs(true)">Atualizar Jobs</button>
                    <button class="wizard-primary" @click="goToJobsFromPreview">Avançar para Jobs</button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Jobs List -->
          <section v-else-if="ui.activeTab.value === 'jobs'" class="panel">
            <div class="jobs-header">
              <h2>Jobs</h2>
              <div class="jobs-controls">
                <select v-model="jobsSortBy" class="form-select">
                  <option value="date_desc">Mais recentes primeiro</option>
                  <option value="date_asc">Mais antigos primeiro</option>
                </select>
                <button class="primary-button secondary" @click="jobs.loadJobs(true)" :disabled="jobsLoading">
                  {{ jobsLoading ? 'Recarregando...' : 'Recarregar agora' }}
                </button>
              </div>
            </div>
            <div v-if="jobsLoading" class="card">
              <p>Carregando jobs...</p>
            </div>
            <div v-else-if="jobs.jobs.value.length === 0" class="card">
              <p>Nenhum job criado ainda.</p>
            </div>
            <div v-else class="jobs-grid">
              <article v-for="job in jobsPaginated" :key="job.jobId" class="card job-card">
                <div class="job-header">
                  <h3>Job #{{ job.jobId }}</h3>
                  <div class="job-header-actions">
                    <span :class="['job-status', normalizeJobStatus(job.status)]">{{ statusLabel(job.status) }}</span>
                    <button class="wizard-secondary job-rerun-button" :disabled="!job.canRerun || rerunJobLoadingId === job.jobId" @click="jobs.rerunJob(job.jobId)">
                      {{ rerunJobLoadingId === job.jobId ? 'Re-running...' : 'Re-run' }}
                    </button>
                    <button class="wizard-secondary job-delete-button" :disabled="deleteJobLoadingId === job.jobId" @click="jobs.deleteJob(job.jobId)">
                      {{ deleteJobLoadingId === job.jobId ? 'Removing...' : 'Remove' }}
                    </button>
                  </div>
                </div>

                <div class="job-progress-track">
                  <div class="job-progress-fill" :style="{ width: `${job.progress || 0}%` }"></div>
                </div>
                <p class="job-progress-text">{{ job.progress || 0 }}%</p>

                <div class="job-steps">
                  <div v-for="stage in JOB_STAGES" :key="`${job.jobId}-${stage}`" :class="['job-step', stageState(job, stage)]">
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
              </article>
            </div>
            <div v-if="jobs.jobs.value.length > 0" class="jobs-pagination">
              <div class="pagination-info">
                <span>Mostrando {{ (jobsCurrentPage - 1) * jobsPageSize + 1 }} até {{ Math.min(jobsCurrentPage * jobsPageSize, jobsSorted.length) }} de {{ jobsSorted.length }} jobs</span>
              </div>
              <div class="pagination-controls">
                <label>
                  Itens por página:
                  <select v-model.number="jobsPageSize" class="form-select">
                    <option :value="5">5</option>
                    <option :value="10">10</option>
                    <option :value="20">20</option>
                    <option :value="50">50</option>
                  </select>
                </label>
                <div class="pagination-buttons">
                  <button @click="jobs.setPage(Math.max(1, jobsCurrentPage - 1))" :disabled="jobsCurrentPage === 1" class="pagination-button">
                    ← Anterior
                  </button>
                  <span class="pagination-text">Página {{ jobsCurrentPage }} de {{ jobsTotalPages }}</span>
                  <button @click="jobs.setPage(Math.min(jobsTotalPages, jobsCurrentPage + 1))" :disabled="jobsCurrentPage === jobsTotalPages" class="pagination-button">
                    Próximo →
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- Templates -->
          <section v-else-if="ui.activeTab.value === 'templates'" class="panel">
            <header>
              <h2>Migration Templates</h2>
              <p>Save and reuse migration configurations</p>
            </header>
            <div class="templates-card">
              <div v-if="templates.templates.value.length === 0" class="empty-state">
                <p>No templates created yet</p>
              </div>
              <div v-else class="templates-list">
                <div v-for="template in templates.templates.value" :key="template.id" class="template-item">
                  <div>
                    <p><strong>{{ template.name }}</strong></p>
                    <small>{{ templates.formatTemplateDate(template.created_at) }}</small>
                  </div>
                  <button class="wizard-secondary" @click="templates.deleteTemplate(template.id)">Delete</button>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  useConnection,
  useMigration,
  useJobs,
  useTemplates,
  useEngine,
  useTheme,
  useUI,
  MIGRATION_FLOW_TABS,
  MIGRATION_FLOW_TABS_FULL,
} from '@/composables'
import {
  Stepper,
  EngineSelector,
  ConnectionForm,
  ThemeSwitcher,
} from '@/components'
import { apiClient } from '@/services/api'

// Composables
const ui = useUI()
const engine = useEngine()
const connection = useConnection()
const migration = useMigration()
const jobs = useJobs()
const templates = useTemplates()
const theme = useTheme()

// Assets
const appLogoUrl = new URL('./assets/logo.png', import.meta.url).href
const logoBasePath = new URL('./assets', import.meta.url).href

// Dashboard Data
const dashboardRecentJobs = [
  {
    job: '#1024 accounts -> clients',
    source: 'accounts',
    target: 'clients',
    status: 'Running',
    statusClass: 'optional',
    progress: '73%',
    records: '91k/124k',
    failed: '138',
    duration: '32m',
    startedAt: 'Today 10:32',
  },
  {
    job: '#1023 orders -> orders',
    source: 'orders',
    target: 'orders',
    status: 'Completed',
    statusClass: 'valid',
    progress: '100%',
    records: '48k/48k',
    failed: '0',
    duration: '18m',
    startedAt: 'Today 09:10',
  },
  {
    job: '#1022 users -> customers',
    source: 'users',
    target: 'customers',
    status: 'Warnings',
    statusClass: 'warn',
    progress: '100%',
    records: '22k/22k',
    failed: '41',
    duration: '11m',
    startedAt: 'Yesterday',
  },
  {
    job: '#1021 invoices -> invoices',
    source: 'invoices',
    target: 'invoices',
    status: 'Failed',
    statusClass: 'warn',
    progress: '42%',
    records: '8k/19k',
    failed: '312',
    duration: '7m',
    startedAt: 'Yesterday',
  },
]

const dashboardIssues = [
  '1 DBRef resolution missing',
  '138 failed records need review',
  '2 required target fields unmapped',
  'PostgreSQL Backup connection is offline',
]

const dashboardActivity = [
  { day: 'Mon', ok: 58, warn: 10 },
  { day: 'Tue', ok: 70, warn: 14 },
  { day: 'Wed', ok: 52, warn: 16 },
  { day: 'Thu', ok: 80, warn: 10 },
  { day: 'Fri', ok: 66, warn: 18 },
  { day: 'Sat', ok: 45, warn: 11 },
  { day: 'Sun', ok: 62, warn: 13 },
]

const sourceDatabases = ref<string[]>([])
const sourceCollections = ref<string[]>([])
const targetDatabases = ref<string[]>([])
const targetCollections = ref<string[]>([])
const sourceDatabasesLoading = ref(false)
const sourceCollectionsLoading = ref(false)
const targetDatabasesLoading = ref(false)
const targetCollectionsLoading = ref(false)
const mappingNavigationLoading = ref(false)

const sourceDatabasesSafe = computed(() =>
  Array.isArray(sourceDatabases.value) ? sourceDatabases.value : []
)
const sourceCollectionsSafe = computed(() =>
  Array.isArray(sourceCollections.value) ? sourceCollections.value : []
)
const targetDatabasesSafe = computed(() =>
  Array.isArray(targetDatabases.value) ? targetDatabases.value : []
)
const targetCollectionsSafe = computed(() =>
  Array.isArray(targetCollections.value) ? targetCollections.value : []
)

const sourceSamples = ref<Record<string, any>[]>([])
const destinationSamples = ref<Record<string, any>[]>([])
const sourceSamplesLoading = ref(false)
const destinationSamplesLoading = ref(false)
const sourceFieldPaths = ref<string[]>([])
const destinationFieldPaths = ref<string[]>([])
const mappedPreviewDocument = ref<Record<string, any> | null>(null)
const useSelectedBaseDocument = ref(false)
const selectedSourceBaseDocumentId = ref('')
const sourceBaseDocument = ref<Record<string, any> | null>(null)
const insertMode = ref<'one' | 'all'>('one')
const extractStarredsEnabled = ref(false)
const mergeDocumentsEnabled = ref(false)
const mergeByField = ref('')
const createJobLoading = ref(false)
const createJobError = ref('')

type MappingRule = {
  id: string
  sourceField: string
  targetField: string
  editTargetName: boolean
  valueFromField: string
  noSource?: boolean
  ruleType: 'direct' | 'concat'
  concatLeftField: string
  concatRightField: string
  concatSeparator: string
  dbRefEnabled: boolean
  dbRefCollection: string
  dbRefForeignField: string
  defaultValueEnabled: boolean
  defaultValueRaw: string
  isCustom: boolean
}

let ruleSequence = 0
const nextRuleId = () => String(++ruleSequence)

const mappingRows = ref<MappingRule[]>([])

const showAddRuleModal = ref(false)
const addRuleMode = ref<'new' | 'concat'>('new')
const addRuleSourceField = ref('')
const addRuleConcatLeft = ref('')
const addRuleConcatRight = ref('')
const addRuleConcatSeparator = ref(' ')
const addRuleTargetField = ref('')
const addRuleNoSource = ref(false)
const addRuleNoSourceDefaultRaw = ref('')
const addRuleError = ref('')

const showDbRefModal = ref(false)
const dbRefEditingRule = ref<MappingRule | null>(null)
const dbRefEnabledDraft = ref(false)
const dbRefCollectionDraft = ref('')
const dbRefForeignFieldDraft = ref('_id')
const dbRefError = ref('')

const showDefaultValueModal = ref(false)
const defaultValueEditingRule = ref<MappingRule | null>(null)
const defaultValueEnabledDraft = ref(false)
const defaultValueRawDraft = ref('')
const defaultValueError = ref('')

// Engine definitions
const availableEngines = [
  {
    name: 'MongoDB',
    type: 'Document database',
    description: 'Collections, nested objects, arrays, DBRef, ObjectId',
    features: ['Collections', 'Nested Objects', 'DBRef'],
    available: true,
    selectable: true,
  },
  {
    name: 'PostgreSQL',
    type: 'Relational database',
    description: 'Schemas, tables, columns, primary keys, constraints',
    features: ['Schemas', 'Constraints', 'JSONB'],
    available: true,
    selectable: true,
  },
  {
    name: 'Keycloak',
    type: 'Identity and Access Management',
    description: 'Realm users migration with configurable field mapping (Keycloak to Keycloak only)',
    features: ['Users', 'Realms', 'Username mapping'],
    available: true,
    selectable: true,
  },
  {
    name: 'MySQL',
    type: 'Relational database',
    description: 'Coming soon',
    features: ['Tables', 'Indexes'],
    available: false,
    selectable: false,
  },
  {
    name: 'Oracle',
    type: 'Enterprise relational database',
    description: 'Coming soon',
    features: ['Enterprise', 'PL/SQL'],
    available: false,
    selectable: false,
  },
  {
    name: 'Redis',
    type: 'Key-value database',
    description: 'Coming soon',
    features: ['KV', 'Streams'],
    available: false,
    selectable: false,
  },
]

// Helper functions
function getCurrentMigrationStep(): number {
  const tabKey = ui.activeTab.value as string
  return MIGRATION_FLOW_TABS.findIndex((t) => t === tabKey)
}

function getMigrationStepDescription(): string {
  const step = MIGRATION_FLOW_TABS_FULL[getCurrentMigrationStep()]
  return step?.label || ''
}

function getPathEngineImage(engineName: string): string {
  const mongoPathImageUrl = new URL('./assets/MongoDB.png', import.meta.url).href
  const postgresPathImageUrl = new URL('./assets/postgres.png', import.meta.url).href
  if (engineName === 'MongoDB') {
    return mongoPathImageUrl
  }
  if (engineName === 'PostgreSQL') {
    return postgresPathImageUrl
  }
  return ''
}

function getEngineLogo(engineName: string): string {
  const logoMap: Partial<Record<string, string>> = {
    MongoDB: new URL('./assets/MongoDB.png', import.meta.url).href,
    PostgreSQL: new URL('./assets/postgres.png', import.meta.url).href,
    Redis: new URL('./assets/redis.png', import.meta.url).href,
  }
  return logoMap[engineName] || ''
}

function getEngineGlyph(engineName: string): string {
  const glyphMap: Record<string, string> = {
    MongoDB: '🍃',
    PostgreSQL: '🐘',
    MySQL: '🐬',
    Oracle: '◉',
    Keycloak: '🛡',
    Redis: '🧠',
  }
  return glyphMap[engineName] || '🗄'
}

function updateSourceConnection(data: any) {
  if (engine.selectedSourceEngine.value === 'Keycloak') {
    Object.assign(connection.keycloakConnectionSource, data)
    return
  }
  Object.assign(connection.mongoConnectionSource, data)
}

function updateTargetConnection(data: any) {
  if (engine.selectedTargetEngine.value === 'Keycloak') {
    Object.assign(connection.keycloakConnectionTarget, data)
    return
  }
  Object.assign(connection.mongoConnectionTarget, data)
}

const sourceTesting = computed(() => {
  return engine.selectedSourceEngine.value === 'Keycloak'
    ? connection.keycloakConnectionSource.testing
    : connection.mongoConnectionSource.testing
})

const sourceStatus = computed(() => {
  return engine.selectedSourceEngine.value === 'Keycloak'
    ? (connection.keycloakConnectionSource.connected ? 'success' : '')
    : (connection.mongoConnectionSource.status as 'success' | 'error' | '')
})

const sourceMessage = computed(() => {
  return engine.selectedSourceEngine.value === 'Keycloak'
    ? connection.keycloakConnectionSource.message
    : connection.mongoConnectionSource.message
})

const sourceConnected = computed(() => {
  return engine.selectedSourceEngine.value === 'Keycloak'
    ? connection.keycloakConnectionSource.connected
    : connection.mongoConnectionSource.status === 'success'
})

const targetTesting = computed(() => {
  return engine.selectedTargetEngine.value === 'Keycloak'
    ? connection.keycloakConnectionTarget.testing
    : connection.mongoConnectionTarget.testing
})

const targetStatus = computed(() => {
  return engine.selectedTargetEngine.value === 'Keycloak'
    ? (connection.keycloakConnectionTarget.connected ? 'success' : '')
    : (connection.mongoConnectionTarget.status as 'success' | 'error' | '')
})

const targetMessage = computed(() => {
  return engine.selectedTargetEngine.value === 'Keycloak'
    ? connection.keycloakConnectionTarget.message
    : connection.mongoConnectionTarget.message
})

const targetConnected = computed(() => {
  return engine.selectedTargetEngine.value === 'Keycloak'
    ? connection.keycloakConnectionTarget.connected
    : connection.mongoConnectionTarget.status === 'success'
})

async function testSourceConnection() {
  if (engine.selectedSourceEngine.value === 'Keycloak') {
    await connection.testKeycloakConnection(connection.keycloakConnectionSource)
    return
  }
  await connection.testMongoConnection(connection.mongoConnectionSource)
}

async function testTargetConnection() {
  if (engine.selectedTargetEngine.value === 'Keycloak') {
    await connection.testKeycloakConnection(connection.keycloakConnectionTarget)
    return
  }
  await connection.testMongoConnection(connection.mongoConnectionTarget)
}

async function loadSourceDatabases() {
  sourceDatabasesLoading.value = true
  try {
    sourceDatabases.value = await connection.loadMongoDatabases(connection.mongoConnectionSource)
  } finally {
    sourceDatabasesLoading.value = false
  }
}

async function loadSourceCollections() {
  if (!connection.mongoConnectionSource.database) {
    return
  }

  sourceCollectionsLoading.value = true
  try {
    sourceCollections.value = await connection.loadMongoCollections(connection.mongoConnectionSource)
  } finally {
    sourceCollectionsLoading.value = false
  }
}

async function loadTargetDatabases() {
  targetDatabasesLoading.value = true
  try {
    targetDatabases.value = await connection.loadMongoDatabases(connection.mongoConnectionTarget)
  } finally {
    targetDatabasesLoading.value = false
  }
}

async function loadTargetCollections() {
  if (!connection.mongoConnectionTarget.database) {
    return
  }

  targetCollectionsLoading.value = true
  try {
    targetCollections.value = await connection.loadMongoCollections(connection.mongoConnectionTarget)
  } finally {
    targetCollectionsLoading.value = false
  }
}

const sourceDocumentForMapping = computed<Record<string, any> | null>(() => {
  if (useSelectedBaseDocument.value && sourceBaseDocument.value) {
    return sourceBaseDocument.value
  }
  return sourceSamples.value.length > 0 ? sourceSamples.value[0] : null
})

const readValueByPath = (value: any, path: string) => {
  return path.split('.').reduce((currentValue, segment) => {
    if (currentValue === null || currentValue === undefined) {
      return undefined
    }
    return currentValue[segment]
  }, value)
}

const writeValueByPath = (target: Record<string, any>, path: string, value: any) => {
  const segments = path.split('.')
  let cursor = target
  for (let i = 0; i < segments.length; i += 1) {
    const segment = segments[i]
    const isLast = i === segments.length - 1
    if (isLast) {
      cursor[segment] = value
      return
    }
    if (!cursor[segment] || typeof cursor[segment] !== 'object') {
      cursor[segment] = {}
    }
    cursor = cursor[segment]
  }
}

const normalizeManualValue = (value: string) => {
  const trimmedValue = value.trim()
  if (!trimmedValue) return ''
  if (trimmedValue === 'true') return true
  if (trimmedValue === 'false') return false
  if (/^-?\d+(\.\d+)?$/.test(trimmedValue)) return Number(trimmedValue)
  if ((trimmedValue.startsWith('{') && trimmedValue.endsWith('}')) || (trimmedValue.startsWith('[') && trimmedValue.endsWith(']'))) {
    try {
      return JSON.parse(trimmedValue)
    } catch {
      return value
    }
  }
  return value
}

const extractFieldPaths = (value: any, prefix = ''): string[] => {
  if (value === null || value === undefined) return prefix ? [prefix] : []
  if (Array.isArray(value)) {
    if (value.length === 0) return prefix ? [prefix] : []
    return extractFieldPaths(value[0], prefix)
  }
  if (typeof value !== 'object') return prefix ? [prefix] : []
  const keys = Object.keys(value)
  if (keys.some((key) => key.startsWith('$'))) return prefix ? [prefix] : []

  const paths: string[] = []
  for (const [key, child] of Object.entries(value)) {
    const nextPrefix = prefix ? `${prefix}.${key}` : key
    const childPaths = extractFieldPaths(child, nextPrefix)
    paths.push(...(childPaths.length > 0 ? childPaths : [nextPrefix]))
  }
  return paths
}

const buildMappedDocument = (sourceDocument: Record<string, any>) => {
  const mappedDocument: Record<string, any> = {}
  for (const mapping of mappingRows.value) {
    if (!mapping.targetField) continue

    const computedValue = mapping.ruleType === 'concat'
      ? [
          readValueByPath(sourceDocument, mapping.concatLeftField),
          readValueByPath(sourceDocument, mapping.concatRightField),
        ]
          .filter((item) => item !== null && item !== undefined)
          .map((item) => String(item))
          .join(mapping.concatSeparator)
      : readValueByPath(sourceDocument, mapping.valueFromField || mapping.sourceField)

    const fieldValue = mapping.defaultValueEnabled
      ? normalizeManualValue(mapping.defaultValueRaw)
      : computedValue

    if (mapping.dbRefEnabled && mapping.dbRefCollection) {
      writeValueByPath(mappedDocument, mapping.targetField, {
        $id: fieldValue,
        $ref: mapping.dbRefCollection,
      })
    } else {
      writeValueByPath(mappedDocument, mapping.targetField, fieldValue)
    }
  }
  return mappedDocument
}

const sourceFieldTree = computed(() => {
  return sourceFieldPaths.value.map((path) => {
    const value = sourceDocumentForMapping.value ? readValueByPath(sourceDocumentForMapping.value, path) : undefined
    const type = Array.isArray(value)
      ? 'array'
      : value === null
      ? 'unknown'
      : typeof value === 'object'
      ? 'object'
      : typeof value
    return {
      path,
      depth: path.split('.').length - 1,
      type,
      typeClass: `type-${type === 'string' || type === 'array' || type === 'object' ? type : 'string'}`,
    }
  })
})

const targetFieldList = computed(() => {
  const merged = new Set<string>([
    ...destinationFieldPaths.value,
    ...mappingRows.value.map((row) => row.targetField).filter((field) => field.trim().length > 0),
  ])
  return Array.from(merged).map((path) => ({
    path,
    type: 'varchar',
    typeClass: 'type-string',
  }))
})

const mappingTableRows = computed(() => {
  return mappingRows.value.map((row, idx) => ({
    index: idx + 1,
    isFirst: idx === 0,
    isLast: idx === mappingRows.value.length - 1,
    model: row,
    typeLabel: 'string -> varchar',
    transform: row.defaultValueEnabled
      ? 'Default Value'
      : row.dbRefEnabled
      ? 'DBRef'
      : row.ruleType === 'concat'
      ? 'Concatenate'
      : 'None',
    required: idx < 3,
    status: row.targetField ? 'Valid' : 'Optional',
    statusClass: row.targetField ? 'valid' : 'optional',
  }))
})

const sourceCodeLines = computed(() => JSON.stringify(sourceDocumentForMapping.value || {}, null, 2).split('\n'))
const mappedCodeLines = computed(() => JSON.stringify(buildMappedDocument(sourceDocumentForMapping.value || {}), null, 2).split('\n'))
const mappedRequiredCount = computed(() => mappingTableRows.value.filter((row) => row.required && row.model.targetField).length)
const optionalUnmappedCount = computed(() => mappingTableRows.value.filter((row) => !row.required && !row.model.targetField).length)
const hasDbRefWarning = computed(() => mappingRows.value.some((row) => row.dbRefEnabled && !row.dbRefCollection))
const hasDefaultValueWarning = computed(() => mappingRows.value.some((row) => row.defaultValueEnabled && !row.defaultValueRaw.trim()))

const formatPreviewValue = (value: any) => {
  if (value === undefined) return 'undefined'
  if (value === null) return 'null'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const previewSourceFields = computed(() => {
  if (!sourceDocumentForMapping.value) return []
  return sourceFieldPaths.value.map((path) => ({
    path,
    value: formatPreviewValue(readValueByPath(sourceDocumentForMapping.value, path)),
  }))
})

const previewMappedFields = computed(() => {
  if (!sourceDocumentForMapping.value) return []
  return mappingRows.value
    .filter((mapping) => mapping.targetField)
    .map((mapping) => {
      const computedValue = mapping.ruleType === 'concat'
        ? [
            readValueByPath(sourceDocumentForMapping.value, mapping.concatLeftField),
            readValueByPath(sourceDocumentForMapping.value, mapping.concatRightField),
          ]
            .filter((item) => item !== null && item !== undefined)
            .map((item) => String(item))
            .join(mapping.concatSeparator)
        : readValueByPath(sourceDocumentForMapping.value, mapping.valueFromField || mapping.sourceField)

      const value = mapping.defaultValueEnabled
        ? normalizeManualValue(mapping.defaultValueRaw)
        : (mapping.dbRefEnabled && mapping.dbRefCollection
          ? { $id: computedValue, $ref: mapping.dbRefCollection }
          : computedValue)

      return {
        path: mapping.targetField,
        value: formatPreviewValue(value),
        mode: mapping.ruleType === 'concat' || mapping.editTargetName ? 'manual' : 'mapped',
      }
    })
})

const hasStarredsArray = computed(() => {
  if (!sourceDocumentForMapping.value) return false
  const value = readValueByPath(sourceDocumentForMapping.value, 'starreds')
  return Array.isArray(value)
})

const mergeFieldOptions = computed(() => {
  return Array.from(new Set(mappingRows.value.map((row) => row.targetField.trim()).filter((field) => field.length > 0)))
})

const JOB_STAGES = ['pending', 'loading_source', 'mapping_fields', 'inserting_documents', 'done'] as const

const jobsLoading = computed(() => jobs.uiState.value.loading)
const rerunJobLoadingId = computed(() => jobs.uiState.value.rerunLoadingId)
const deleteJobLoadingId = computed(() => jobs.uiState.value.deleteLoadingId)

const jobsSortBy = computed({
  get: () => jobs.uiState.value.sortBy,
  set: (value: 'date_desc' | 'date_asc') => jobs.setSortBy(value),
})

const jobsCurrentPage = computed({
  get: () => jobs.uiState.value.currentPage,
  set: (value: number) => jobs.setPage(value),
})

const jobsPageSize = computed({
  get: () => jobs.uiState.value.pageSize,
  set: (value: number) => jobs.setPageSize(value),
})

const jobsSorted = computed(() => jobs.jobsSorted.value)
const jobsPaginated = computed(() => jobs.jobsPaginated.value)
const jobsTotalPages = computed(() => Math.max(1, jobs.jobsTotalPages.value || 1))

const normalizeJobStatus = (status: string) => {
  if (JOB_STAGES.includes(status as (typeof JOB_STAGES)[number])) {
    return status
  }
  if (status === 'running') {
    return 'inserting_documents'
  }
  return status
}

const statusLabel = (status: string) => {
  const normalized = normalizeJobStatus(status)
  const labels: Record<string, string> = {
    pending: 'pending',
    loading_source: 'loading source',
    mapping_fields: 'mapping fields',
    inserting_documents: 'inserting documents',
    done: 'done',
    failed: 'failed',
  }
  return labels[normalized] || normalized
}

const stageLabel = (stage: string) => {
  const labels: Record<string, string> = {
    pending: 'Queue',
    loading_source: 'Source load',
    mapping_fields: 'Mapping',
    inserting_documents: 'Insert',
    done: 'Done',
  }
  return labels[stage] || stage
}

const stageState = (job: any, stage: string) => {
  const normalized = normalizeJobStatus(job.status)
  const currentIdx = JOB_STAGES.indexOf(normalized as (typeof JOB_STAGES)[number])
  const stageIdx = JOB_STAGES.indexOf(stage as (typeof JOB_STAGES)[number])

  if (normalized === 'failed') {
    return 'pending'
  }

  if (currentIdx === -1 || stageIdx === -1) {
    return 'pending'
  }

  if (stageIdx < currentIdx) {
    return 'done'
  }

  if (stageIdx === currentIdx) {
    return normalized === 'done' ? 'done' : 'active'
  }

  return 'pending'
}

const jobNoOutputHint = (job: any) => {
  const result = job.result
  if (!result) {
    return ''
  }

  const processed = result.processed ?? 0
  const inserted = result.inserted ?? 0
  const merged = result.merged ?? 0
  const skipped = result.skipped ?? 0

  if (processed > 0 && inserted === 0 && merged === 0) {
    if (skipped > 0) {
      return 'Nenhum documento novo foi gravado. Todos foram ignorados (ex.: duplicidade de chave).'
    }
    return 'Nenhum documento foi gerado para insercao. Revise filtros/flatten e os campos mapeados.'
  }

  return ''
}

const buildKeycloakPayload = (config: any) => ({
  baseUrl: config.baseUrl.trim(),
  realm: config.realm.trim(),
  authMode: config.authMode,
  clientId: config.clientId.trim(),
  clientSecret: config.authMode === 'client_credentials' ? config.clientSecret : null,
  username: config.authMode === 'password' ? config.username.trim() : null,
  password: config.authMode === 'password' ? config.password : null,
})

const applyMongoCredentials = (connectionString: string, username: string, password: string) => {
  const user = username.trim()
  const pass = password.trim()
  if (!user && !pass) {
    return connectionString
  }

  const schemeIndex = connectionString.indexOf('://')
  if (schemeIndex < 0) {
    return connectionString
  }

  const prefix = connectionString.slice(0, schemeIndex + 3)
  const rest = connectionString.slice(schemeIndex + 3)
  const hostAndPath = rest.includes('@') ? rest.split('@').slice(1).join('@') : rest

  const encodedUser = encodeURIComponent(user)
  const encodedPass = encodeURIComponent(pass)
  const credentials = user ? `${encodedUser}:${encodedPass}` : `:${encodedPass}`

  return `${prefix}${credentials}@${hostAndPath}`
}

const buildMongoConnectionPayload = (config: any) => ({
  connectionString: config.authEnabled
    ? applyMongoCredentials(config.connectionString, config.username, config.password)
    : config.connectionString,
  authSource: config.authEnabled ? (config.authSource.trim() || null) : null,
  database: config.database,
  collection: config.collection,
})

const buildMigrationConfig = () => {
  const fieldMapping: Record<string, string> = {}
  const manualMapping: Record<string, any> = {}
  const concatRules: Array<{ sourceFields: string[]; targetField: string; separator: string }> = []
  const dbRefRules: Array<{ targetField: string; fromCollection: string; foreignField: string }> = []
  const flattenConfig: Array<{ field: string; mode: 'preserve' | 'explode' }> = []
  const filterRules: Array<{ field: string; op: 'eq' | 'truthy'; value?: any }> = []

  for (const row of mappingRows.value) {
    const targetField = row.targetField.trim()
    if (!targetField) {
      continue
    }

    if (row.defaultValueEnabled) {
      manualMapping[targetField] = normalizeManualValue(row.defaultValueRaw)
      continue
    }

    if (row.ruleType === 'concat') {
      concatRules.push({
        sourceFields: [row.concatLeftField, row.concatRightField],
        targetField,
        separator: row.concatSeparator,
      })
      if (row.dbRefEnabled && row.dbRefCollection) {
        dbRefRules.push({
          targetField,
          fromCollection: row.dbRefCollection,
          foreignField: row.dbRefForeignField || '_id',
        })
      }
      continue
    }

    const valueFromField = (row.valueFromField || row.sourceField).trim()
    if (!valueFromField) {
      continue
    }

    fieldMapping[valueFromField] = targetField
    if (row.dbRefEnabled && row.dbRefCollection) {
      dbRefRules.push({
        targetField,
        fromCollection: row.dbRefCollection,
        foreignField: row.dbRefForeignField || '_id',
      })
    }
  }

  if (extractStarredsEnabled.value && hasStarredsArray.value) {
    flattenConfig.push({ field: 'starreds', mode: 'explode' })
    filterRules.push({ field: 'starreds.starred', op: 'eq', value: true })
    if (manualMapping._class === undefined) {
      manualMapping._class = 'Favorites'
    }
    const now = new Date().toISOString()
    if (manualMapping.createdAt === undefined) {
      manualMapping.createdAt = now
    }
    if (manualMapping.updatedAt === undefined) {
      manualMapping.updatedAt = now
    }
  }

  const sourcePayload = buildMongoConnectionPayload(connection.mongoConnectionSource)
  const targetPayload = buildMongoConnectionPayload(connection.mongoConnectionTarget)

  return {
    migrationName: `Migracao ${new Date().toISOString()}`,
    source: {
      connectionString: sourcePayload.connectionString,
      database: connection.mongoConnectionSource.database,
      collection: connection.mongoConnectionSource.collection,
      authSource: sourcePayload.authSource,
    },
    target: {
      connectionString: targetPayload.connectionString,
      database: connection.mongoConnectionTarget.database,
      collection: connection.mongoConnectionTarget.collection,
      authSource: targetPayload.authSource,
    },
    sourceBaseDocumentId: useSelectedBaseDocument.value ? (selectedSourceBaseDocumentId.value || null) : null,
    fieldMapping,
    manualMapping,
    concatRules,
    dbRefRules,
    mergeByField: mergeDocumentsEnabled.value ? mergeByField.value.trim() : null,
    lookups: [],
    flattenConfig,
    filterRules,
  }
}

const buildKeycloakMigrationConfig = () => {
  const fieldMapping: Record<string, string> = {}
  for (const row of mappingRows.value) {
    const sourceField = (row.valueFromField || row.sourceField || '').trim()
    const targetField = (row.targetField || '').trim()
    if (!sourceField || !targetField || row.ruleType !== 'direct' || row.noSource) {
      continue
    }
    fieldMapping[sourceField] = targetField
  }

  return {
    migrationType: 'keycloak',
    migrationName: `Migracao Keycloak ${new Date().toISOString()}`,
    source: buildKeycloakPayload(connection.keycloakConnectionSource),
    target: buildKeycloakPayload(connection.keycloakConnectionTarget),
    usernameSourceField: migration.keycloakUsernameSourceField.value || 'username',
    fieldMapping,
  }
}

const syncMappingsFromSamples = () => {
  sourceFieldPaths.value = sourceDocumentForMapping.value ? extractFieldPaths(sourceDocumentForMapping.value) : []
  destinationFieldPaths.value = destinationSamples.value.length > 0 ? extractFieldPaths(destinationSamples.value[0]) : []
  const destinationHasSchema = destinationFieldPaths.value.length > 0

  const customRules = mappingRows.value.filter((item) => item.isCustom)
  const nonCustomRules = mappingRows.value.filter((item) => !item.isCustom)
  const currentMappings = new Map(nonCustomRules.map((item) => [item.sourceField, item.targetField]))
  const currentEditTargetFlags = new Map(nonCustomRules.map((item) => [item.sourceField, item.editTargetName]))
  const currentDbRefEnabled = new Map(nonCustomRules.map((item) => [item.sourceField, item.dbRefEnabled]))
  const currentDbRefCollection = new Map(nonCustomRules.map((item) => [item.sourceField, item.dbRefCollection]))
  const currentDbRefForeignField = new Map(nonCustomRules.map((item) => [item.sourceField, item.dbRefForeignField]))
  const currentDefaultEnabled = new Map(nonCustomRules.map((item) => [item.sourceField, item.defaultValueEnabled]))
  const currentDefaultRaw = new Map(nonCustomRules.map((item) => [item.sourceField, item.defaultValueRaw]))
  const currentIds = new Map(nonCustomRules.map((item) => [item.sourceField, item.id]))

  const directRules = sourceFieldPaths.value.map((field) => {
    return {
      id: currentIds.get(field) ?? nextRuleId(),
      sourceField: field,
      targetField: currentMappings.get(field) ?? (destinationHasSchema ? (destinationFieldPaths.value.includes(field) ? field : '') : field),
      editTargetName: currentEditTargetFlags.get(field) ?? false,
      valueFromField: field,
      noSource: false,
      ruleType: 'direct' as const,
      concatLeftField: '',
      concatRightField: '',
      concatSeparator: ' ',
      dbRefEnabled: currentDbRefEnabled.get(field) ?? false,
      dbRefCollection: currentDbRefCollection.get(field) ?? '',
      dbRefForeignField: currentDbRefForeignField.get(field) ?? '_id',
      defaultValueEnabled: currentDefaultEnabled.get(field) ?? false,
      defaultValueRaw: currentDefaultRaw.get(field) ?? '',
      isCustom: false,
    }
  })

  const filteredCustomRules = customRules.filter((rule) => {
    if (rule.noSource) return true
    if (rule.ruleType === 'concat') {
      return sourceFieldPaths.value.includes(rule.concatLeftField) && sourceFieldPaths.value.includes(rule.concatRightField)
    }
    return sourceFieldPaths.value.includes(rule.valueFromField)
  })

  mappingRows.value = [...directRules, ...filteredCustomRules]
}

const openAddRuleModal = () => {
  showAddRuleModal.value = true
  addRuleError.value = ''
  addRuleMode.value = 'new'
  addRuleSourceField.value = sourceFieldPaths.value[0] || ''
  addRuleConcatLeft.value = sourceFieldPaths.value[0] || ''
  addRuleConcatRight.value = sourceFieldPaths.value[1] || sourceFieldPaths.value[0] || ''
  addRuleConcatSeparator.value = ' '
  addRuleTargetField.value = ''
  addRuleNoSource.value = false
  addRuleNoSourceDefaultRaw.value = ''
}

const closeAddRuleModal = () => {
  showAddRuleModal.value = false
  addRuleError.value = ''
}

const submitAddRule = () => {
  addRuleError.value = ''
  const targetField = addRuleTargetField.value.trim()
  if (!targetField) {
    addRuleError.value = 'Informe o nome do campo no target.'
    return
  }

  if (addRuleMode.value === 'new') {
    const sourceField = addRuleNoSource.value ? '(novo)' : addRuleSourceField.value
    mappingRows.value.push({
      id: nextRuleId(),
      sourceField,
      targetField,
      editTargetName: true,
      valueFromField: addRuleNoSource.value ? '' : addRuleSourceField.value,
      noSource: addRuleNoSource.value,
      ruleType: 'direct',
      concatLeftField: '',
      concatRightField: '',
      concatSeparator: ' ',
      dbRefEnabled: false,
      dbRefCollection: '',
      dbRefForeignField: '_id',
      defaultValueEnabled: addRuleNoSource.value,
      defaultValueRaw: addRuleNoSource.value ? addRuleNoSourceDefaultRaw.value : '',
      isCustom: true,
    })
    closeAddRuleModal()
    return
  }

  mappingRows.value.push({
    id: nextRuleId(),
    sourceField: `${addRuleConcatLeft.value} + ${addRuleConcatRight.value}`,
    targetField,
    editTargetName: true,
    valueFromField: addRuleConcatLeft.value,
    noSource: false,
    ruleType: 'concat',
    concatLeftField: addRuleConcatLeft.value,
    concatRightField: addRuleConcatRight.value,
    concatSeparator: addRuleConcatSeparator.value,
    dbRefEnabled: false,
    dbRefCollection: '',
    dbRefForeignField: '_id',
    defaultValueEnabled: false,
    defaultValueRaw: '',
    isCustom: true,
  })
  closeAddRuleModal()
}

const moveMappingRule = (rowIndex: number, direction: -1 | 1) => {
  const targetIndex = rowIndex + direction
  if (rowIndex < 0 || targetIndex < 0 || rowIndex >= mappingRows.value.length || targetIndex >= mappingRows.value.length) {
    return
  }
  const [rule] = mappingRows.value.splice(rowIndex, 1)
  if (!rule) return
  mappingRows.value.splice(targetIndex, 0, rule)
}

const removeRule = (rule: MappingRule) => {
  if (!rule.isCustom) {
    rule.targetField = ''
    return
  }
  mappingRows.value = mappingRows.value.filter((item) => item !== rule)
}

const setDirectRuleSourceField = (rule: MappingRule, sourceField: string) => {
  if (rule.ruleType !== 'direct' || rule.noSource) {
    return
  }
  rule.sourceField = sourceField
  rule.valueFromField = sourceField
}

const openDbRefModal = (rule: MappingRule) => {
  dbRefEditingRule.value = rule
  dbRefEnabledDraft.value = rule.dbRefEnabled
  dbRefCollectionDraft.value = rule.dbRefCollection
  dbRefForeignFieldDraft.value = rule.dbRefForeignField || '_id'
  dbRefError.value = ''
  showDbRefModal.value = true
}

const closeDbRefModal = () => {
  showDbRefModal.value = false
  dbRefEditingRule.value = null
  dbRefError.value = ''
}

const saveDbRefRule = () => {
  if (!dbRefEditingRule.value) return
  if (dbRefEnabledDraft.value && !dbRefCollectionDraft.value.trim()) {
    dbRefError.value = 'Informe a collection de referencia para DBRef.'
    return
  }
  dbRefEditingRule.value.dbRefEnabled = dbRefEnabledDraft.value
  dbRefEditingRule.value.dbRefCollection = dbRefCollectionDraft.value.trim()
  dbRefEditingRule.value.dbRefForeignField = (dbRefForeignFieldDraft.value || '_id').trim()
  closeDbRefModal()
}

const openDefaultValueModal = (rule: MappingRule) => {
  defaultValueEditingRule.value = rule
  defaultValueEnabledDraft.value = rule.defaultValueEnabled
  defaultValueRawDraft.value = rule.defaultValueRaw
  defaultValueError.value = ''
  showDefaultValueModal.value = true
}

const closeDefaultValueModal = () => {
  showDefaultValueModal.value = false
  defaultValueEditingRule.value = null
  defaultValueError.value = ''
}

const saveDefaultValueRule = () => {
  if (!defaultValueEditingRule.value) return
  if (defaultValueEnabledDraft.value && !defaultValueRawDraft.value.trim()) {
    defaultValueError.value = 'Informe o valor padrao para este campo.'
    return
  }
  defaultValueEditingRule.value.defaultValueEnabled = defaultValueEnabledDraft.value
  defaultValueEditingRule.value.defaultValueRaw = defaultValueRawDraft.value
  closeDefaultValueModal()
}

const getDocumentId = (item: Record<string, any>): string => {
  const rawId = item?._id
  if (!rawId) return ''
  if (typeof rawId === 'string') return rawId
  if (typeof rawId === 'object' && typeof rawId.$oid === 'string') return rawId.$oid
  return ''
}

const selectSourceBaseDocument = (item: Record<string, any>) => {
  const id = getDocumentId(item)
  selectedSourceBaseDocumentId.value = id
  sourceBaseDocument.value = id ? item : null
  syncMappingsFromSamples()
}

const viewSourceSample = async () => {
  if (engine.selectedSourceEngine.value !== 'MongoDB') {
    return
  }
  sourceSamplesLoading.value = true
  sourceSamples.value = []
  sourceBaseDocument.value = null
  selectedSourceBaseDocumentId.value = ''
  try {
    const response = await apiClient.loadMongoSamples({
      connectionString: connection.mongoConnectionSource.connectionString,
      database: connection.mongoConnectionSource.database,
      collection: connection.mongoConnectionSource.collection,
      authEnabled: connection.mongoConnectionSource.authEnabled,
      username: connection.mongoConnectionSource.username,
      password: connection.mongoConnectionSource.password,
      authSource: connection.mongoConnectionSource.authSource,
      limit: 10,
    })
    sourceSamples.value = response.data.items || response.data.samples || []
    syncMappingsFromSamples()
    if (sourceDocumentForMapping.value) {
      mappedPreviewDocument.value = buildMappedDocument(sourceDocumentForMapping.value)
    }
  } finally {
    sourceSamplesLoading.value = false
  }
}

const viewDestinationSample = async () => {
  if (engine.selectedTargetEngine.value !== 'MongoDB') {
    return
  }
  destinationSamplesLoading.value = true
  destinationSamples.value = []
  try {
    const response = await apiClient.loadMongoSamples({
      connectionString: connection.mongoConnectionTarget.connectionString,
      database: connection.mongoConnectionTarget.database,
      collection: connection.mongoConnectionTarget.collection,
      authEnabled: connection.mongoConnectionTarget.authEnabled,
      username: connection.mongoConnectionTarget.username,
      password: connection.mongoConnectionTarget.password,
      authSource: connection.mongoConnectionTarget.authSource,
      limit: 10,
    })
    destinationSamples.value = response.data.items || response.data.samples || []
    syncMappingsFromSamples()
    if (sourceDocumentForMapping.value) {
      mappedPreviewDocument.value = buildMappedDocument(sourceDocumentForMapping.value)
    }
  } finally {
    destinationSamplesLoading.value = false
  }
}

const mapData = () => {
  if (!sourceDocumentForMapping.value) {
    mappedPreviewDocument.value = null
    return
  }
  mappedPreviewDocument.value = buildMappedDocument(sourceDocumentForMapping.value)
  ui.setActiveTab('preview')
}

const goToJobsFromPreview = async () => {
  ui.setActiveTab('jobs')
  await jobs.loadJobs(true)
}

const createInsertJob = async () => {
  createJobError.value = ''
  if (engine.selectedSourceEngine.value === 'Keycloak' && engine.selectedTargetEngine.value === 'Keycloak') {
    if (!connection.keycloakConnectionSource.connected || !connection.keycloakConnectionTarget.connected) {
      createJobError.value = 'Conecte e valide source e target Keycloak antes de executar.'
      return
    }
    if (!migration.keycloakUsernameSourceField.value.trim()) {
      createJobError.value = 'Selecione o campo de origem para username.'
      return
    }

    createJobLoading.value = true
    try {
      await apiClient.executeKeycloakMigration({
        config: buildKeycloakMigrationConfig(),
        maxDocuments: insertMode.value === 'one' ? 1 : null,
      })
      await jobs.loadJobs(true)
      ui.setActiveTab('jobs')
      jobs.startJobsPolling()
    } catch (error: any) {
      createJobError.value = error?.response?.data?.detail || error?.message || 'Falha ao criar job de migracao Keycloak.'
    } finally {
      createJobLoading.value = false
    }
    return
  }

  if (!connection.mongoConnectionSource.database || !connection.mongoConnectionSource.collection) {
    createJobError.value = 'Selecione database e collection de origem.'
    return
  }
  if (!connection.mongoConnectionTarget.database || !connection.mongoConnectionTarget.collection) {
    createJobError.value = 'Selecione database e collection de destino.'
    return
  }

  const config = buildMigrationConfig()
  if (Object.keys(config.fieldMapping).length === 0 && Object.keys(config.manualMapping).length === 0 && config.concatRules.length === 0) {
    createJobError.value = 'Configure ao menos um mapeamento antes de inserir.'
    return
  }
  if (mergeDocumentsEnabled.value && !mergeByField.value.trim()) {
    createJobError.value = 'Selecione o campo de mesclagem.'
    return
  }

  createJobLoading.value = true
  try {
    await apiClient.executeMigration({
      config,
      maxDocuments: insertMode.value === 'one' ? 1 : null,
    })
    await jobs.loadJobs(true)
    ui.setActiveTab('jobs')
    jobs.startJobsPolling()
  } catch (error: any) {
    createJobError.value = error?.response?.data?.detail || error?.message || 'Falha ao criar job de insercao.'
  } finally {
    createJobLoading.value = false
  }
}

const goToMappingFromConnections = async () => {
  mappingNavigationLoading.value = true
  try {
    if (engine.selectedSourceEngine.value === 'MongoDB' && sourceSamples.value.length === 0) {
      await viewSourceSample()
    }
    if (engine.selectedTargetEngine.value === 'MongoDB' && destinationSamples.value.length === 0) {
      await viewDestinationSample()
    }
  } catch (error) {
    console.warn('Falha ao precarregar samples para mapping, prosseguindo mesmo assim.', error)
  } finally {
    mappingNavigationLoading.value = false
    ui.setActiveTab('mapping')
  }
}

function executeJob() {
  // Execute migration job
  console.log('Executing job...')
  ui.nextTab()
}

// Initialize theme on mount
onMounted(() => {
  theme.loadThemeFromStorage()
  jobs.startJobsPolling()
  templates.loadTemplates()
})
</script>

<style scoped>
/* Light theme dark mode styling will be applied via data-theme attribute */
</style>

<style>
/* Global theme variables are applied via theme.css */

/* Import theme.css is already done in main.ts */
* {
  color-scheme: var(--color-scheme, dark);
}

html {
  background: var(--color-bg-primary, #0f172a);
  color: var(--color-text-primary, #f8fafc);
}

body {
  background: var(--color-bg-primary, #0f172a);
  color: var(--color-text-primary, #f8fafc);
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Layout */
#app {
  width: 100%;
  min-height: 100vh;
}

.global-shell {
  display: grid;
  grid-template-columns: 200px 1fr;
  height: 100vh;
  background: var(--color-bg-primary, #0f172a);
  color: var(--color-text-primary, #f8fafc);
  border: none;
  border-radius: 0;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

.global-sidebar {
  background: var(--color-bg-secondary, #0b1220);
  border-right: 1px solid var(--color-border, #334155);
  padding: 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.global-logo {
  display: flex;
  gap: 10px;
  align-items: center;
}

.global-logo-image {
  width: 34px;
  height: 34px;
}

.global-logo strong {
  display: block;
  font-size: 0.9rem;
  color: var(--color-text-primary, #f8fafc);
}

.global-logo small {
  display: block;
  color: var(--color-text-muted, #94a3b8);
  letter-spacing: 0.08em;
}

.global-nav {
  display: grid;
  gap: 6px;
}

.global-nav-item {
  text-align: left;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-muted, #94a3b8);
  padding: 9px 10px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.global-nav-item:hover {
  background: rgba(34, 197, 94, 0.1);
}

.global-nav-item.active {
  color: var(--color-success-light, #dcfce7);
  background: var(--color-success-bg, rgba(34, 197, 94, 0.15));
  border-color: var(--color-success-border, rgba(34, 197, 94, 0.35));
}

.global-sidebar-footer {
  margin-top: auto;
  display: grid;
  gap: 10px;
}

.global-env,
.global-user {
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 10px;
  color: var(--color-text-muted, #94a3b8);
  font-size: 0.82rem;
  background: var(--color-bg-tertiary, rgba(17, 24, 39, 0.8));
}

.global-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary, #0f172a);
  overflow: hidden;
}

.global-main-header {
  background: radial-gradient(circle at 30% 0%, rgba(6, 182, 212, 0.07), transparent 36%), 
    var(--color-bg-primary, #0f172a);
  border-bottom: 1px solid var(--color-border, #334155);
  padding: 18px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.global-topbar-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.global-icon-button {
  border: 1px solid var(--color-border, #334155);
  background: var(--color-bg-tertiary, rgba(31, 41, 55, 0.9));
  color: var(--color-text-secondary, #cbd5e1);
  border-radius: 9px;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 0.9rem;
}

.global-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--color-success, #22c55e);
  color: var(--color-success-dark, #052e16);
  font-weight: 700;
}

.migration-flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.migration-flow-copy h2 {
  margin: 0;
  font-size: 1.3rem;
  color: var(--color-text-primary, #f8fafc);
}

.migration-flow-copy p {
  margin: 4px 0 0;
  color: var(--color-text-muted, #94a3b8);
}

/* Content Area */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
}

.panel {
  background: var(--color-bg-secondary, #111827);
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  padding: 20px;
  display: grid;
  gap: 20px;
}

/* Dashboard */
.dashboard-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.dashboard-topbar h2 {
  margin: 0;
}

.dashboard-topbar p {
  margin: 4px 0 0;
  color: var(--color-text-muted, #94a3b8);
}

.dashboard-metrics {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  margin-bottom: 12px;
}

.dashboard-metric-card {
  border: 1px solid var(--color-border, #334155);
  background: linear-gradient(180deg, var(--color-bg-primary, #0f172a) 0%, var(--color-bg-secondary, #111827) 100%);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 4px;
}

.dashboard-label {
  margin: 0;
  color: var(--color-text-muted, #94a3b8);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.dashboard-metric-card strong {
  font-size: 1.42rem;
  line-height: 1.1;
}

.dashboard-metric-card span {
  color: var(--color-info, #67e8f9);
  font-size: 0.82rem;
}

.dashboard-middle-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}

.dashboard-active-card,
.dashboard-health-card,
.dashboard-jobs-card,
.dashboard-issues-card,
.dashboard-actions-card {
  border: 1px solid var(--color-border, #334155);
  background: linear-gradient(180deg, var(--color-bg-secondary, #111827) 0%, rgba(31, 41, 55, 1) 100%);
  border-radius: 14px;
  padding: 14px;
}

.dashboard-card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.dashboard-card-title-row h3 {
  margin: 0;
}

.dashboard-flow {
  margin: 8px 0 0;
  color: var(--color-text-muted, #94a3b8);
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.84rem;
}

.dashboard-progress-track {
  height: 10px;
  border-radius: 999px;
  background: var(--color-bg-primary, #0f172a);
  border: 1px solid var(--color-border, #334155);
  margin-top: 12px;
  overflow: hidden;
}

.dashboard-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-success, #22c55e) 0%, var(--color-info, #06b6d4) 100%);
}

.dashboard-progress-text {
  margin: 6px 0 0;
  color: var(--color-text-secondary, #cbd5e1);
  font-weight: 600;
}

.dashboard-kpi-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 10px;
}

.dashboard-kpi-grid div {
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  background: var(--color-bg-primary, #0f172a);
  padding: 8px 10px;
  display: grid;
  gap: 3px;
}

.dashboard-kpi-grid span {
  color: var(--color-text-muted, #94a3b8);
  font-size: 0.75rem;
}

.dashboard-kpi-grid strong {
  font-size: 0.92rem;
}

.dashboard-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.dashboard-health-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.dashboard-health-list li {
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  background: var(--color-bg-primary, #0f172a);
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary, #cbd5e1);
  font-size: 0.84rem;
}

.dashboard-health-list em {
  color: var(--color-text-muted, #94a3b8);
  font-style: normal;
  margin-left: auto;
  font-size: 0.78rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.ok { background: var(--color-success, #22c55e); }
.dot.warn { background: var(--color-warning, #f59e0b); }
.dot.err { background: var(--color-error, #ef4444); }

.dashboard-jobs-card {
  margin-bottom: 10px;
}

.dashboard-table-wrap {
  overflow: auto;
  margin-top: 10px;
}

.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}

.dashboard-table th,
.dashboard-table td {
  padding: 8px;
  border-bottom: 1px solid var(--color-border, #334155);
  font-size: 0.8rem;
  white-space: nowrap;
}

.dashboard-table th {
  color: var(--color-text-muted, #94a3b8);
  text-transform: uppercase;
  font-size: 0.68rem;
  letter-spacing: 0.04em;
}

.dashboard-bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.dashboard-issues-card ul {
  margin: 10px 0 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
  color: var(--color-text-primary, #f1f5f9);
}

.dashboard-quick-actions {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.dashboard-activity-chart {
  margin-top: 12px;
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  padding: 10px;
  background: var(--color-bg-primary, #0f172a);
}

.dashboard-activity-chart h4 {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-secondary, #cbd5e1);
}

/* Engines Section */
.engines-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.wizard-topbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.wizard-icon-button {
  border: 1px solid var(--color-border, #334155);
  background: var(--color-bg-tertiary, rgba(31, 41, 55, 0.9));
  color: var(--color-text-secondary, #cbd5e1);
  border-radius: 9px;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}

.wizard-icon-button:hover {
  background: rgba(34, 197, 94, 0.1);
}

.engines-header h2 {
  margin: 0;
}

.engines-header p {
  margin: 4px 0 0;
  color: var(--color-text-muted, #94a3b8);
}

.engines-path-card,
.engines-available-card {
  border: 1px solid var(--color-border, #334155);
  border-radius: 14px;
  background: linear-gradient(180deg, var(--color-bg-secondary, #111827) 0%, rgba(31, 41, 55, 1) 100%);
  padding: 14px;
  margin-bottom: 14px;
}

.engines-path-card h3,
.engines-available-card h3 {
  margin: 0;
}

.engines-path-row {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 80px 1fr;
  gap: 10px;
  align-items: center;
}

.engine-selected-card {
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  background: var(--color-bg-primary, #0f172a);
  padding: 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 14px;
}

.engine-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.engine-brand-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.engine-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  background: rgba(147, 51, 234, 0.15);
  color: #d8b4fe;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid rgba(147, 51, 234, 0.3);
  white-space: nowrap;
}

.engine-title-with-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.engine-path-image {
  width: 58px;
  height: 58px;
  border-radius: 12px;
  border: 1px solid var(--color-border, #334155);
  background: rgba(15, 23, 42, 0.8);
  object-fit: contain;
  padding: 6px;
}

.engine-path-glyph {
  width: 58px;
  height: 58px;
  font-size: 1.45rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.engine-brand-logo,
.engine-brand-glyph {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  border: 1px solid var(--color-border, #334155);
  background: rgba(15, 23, 42, 0.8);
}

.engine-brand-logo {
  object-fit: contain;
  padding: 3px;
}

.engine-brand-glyph {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.engine-selected-card h4 {
  margin: 2px 0;
}

.engine-selected-card p {
  margin: 0;
  color: var(--color-text-secondary, #cbd5e1);
  font-weight: 600;
}

.engine-selected-card small {
  color: var(--color-text-muted, #94a3b8);
}

.engine-selected-card.source {
  border-color: rgba(34, 197, 94, 0.45);
}

.engine-selected-card.target {
  border-color: rgba(34, 211, 238, 0.85);
  background: linear-gradient(145deg, rgba(8, 145, 178, 0.42) 0%, rgba(30, 58, 138, 0.55) 52%, rgba(15, 23, 42, 0.98) 100%);
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.25) inset, 0 10px 28px rgba(6, 182, 212, 0.22);
}

.engine-role-badge {
  align-self: flex-start;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.engine-role-badge.source {
  background: rgba(34, 197, 94, 0.16);
  color: #4ade80;
}

.engine-role-badge.target {
  background: rgba(6, 182, 212, 0.16);
  color: var(--color-info, #67e8f9);
}

.engine-path-arrow {
  text-align: center;
  color: var(--color-info, #67e8f9);
  font-size: 1.6rem;
  text-shadow: 0 0 18px rgba(6, 182, 212, 0.45);
}

.engine-compatibility {
  margin-top: 12px;
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  padding: 10px;
  background: var(--color-bg-primary, #0f172a);
}

.engine-compatibility h4 {
  margin: 0;
}

.engine-compatibility ul {
  margin: 10px 0 0;
  padding-left: 18px;
  display: grid;
  gap: 6px;
  color: var(--color-text-secondary, #cbd5e1);
}

.engines-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.engine-card {
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  background: var(--color-bg-primary, #0f172a);
  padding: 12px;
  display: grid;
  gap: 8px;
}

.engine-card.selected {
  border-color: rgba(34, 197, 94, 0.45);
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.2) inset;
}

.engine-card.disabled {
  opacity: 0.66;
}

.engine-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.engine-card h4 {
  margin: 0;
  line-height: 1.2;
}

.engine-card p {
  margin: 0;
  color: var(--color-text-secondary, #cbd5e1);
  font-size: 0.85rem;
}

.engine-card small {
  color: var(--color-text-muted, #94a3b8);
}

.engine-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.engine-tags span {
  border: 1px solid var(--color-border, #334155);
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 0.72rem;
  color: var(--color-text-secondary, #cbd5e1);
}

.engine-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.engine-action-button.active.source {
  background: #0ea5e9;
  border-color: #0284c7;
  color: #e0f2fe;
  box-shadow: 0 10px 22px rgba(14, 165, 233, 0.32);
}

.engine-action-button.active.target {
  background: var(--color-success, #22c55e);
  border-color: #16a34a;
  color: #dcfce7;
  box-shadow: 0 10px 22px rgba(34, 197, 94, 0.3);
}

/* Connections Section */
.connections-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.connections-header-row h2 {
  margin: 0;
}

.migration-mode-control {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.migration-mode-text {
  font-size: 0.9rem;
  color: var(--color-text-secondary, #cbd5e1);
  font-weight: 600;
}

.migration-mode-toggle-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.migration-mode-option {
  font-size: 0.84rem;
  color: var(--color-text-muted, #94a3b8);
  font-weight: 600;
  transition: color 0.2s ease;
}

.migration-mode-option.active {
  color: var(--color-text-primary, #e2e8f0);
}

.migration-mode-control .migration-mode-switch {
  gap: 0;
}

.auth-switch {
  border: 0;
  background: transparent;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.auth-switch-label {
  font-size: 0.76rem;
  color: var(--color-text-secondary, #cbd5e1);
  white-space: nowrap;
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

.connection-inline-status {
  margin: 0;
}

.connections-engine-note {
  margin: 0 0 10px;
  color: var(--color-text-muted, #94a3b8);
}

.connection-field-label {
  display: block;
  margin-top: 10px;
  font-size: 0.9rem;
  color: var(--color-text-secondary, #cbd5e1);
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--color-border, #334155);
  border-radius: 8px;
  margin-top: 6px;
  font-size: 0.95rem;
  background-color: var(--color-bg-primary, #0f172a);
  color: var(--color-text-primary, #e2e8f0);
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: var(--color-info, #06b6d4);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
}

.connection-action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  background: var(--color-success, #22c55e);
  color: #052e16;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.primary-button:hover:not(:disabled) {
  background: #16a34a;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.samples-list {
  margin-top: 16px;
  padding: 12px;
  background: #0b1220;
  border: 1px solid var(--color-border, #334155);
  border-radius: 8px;
}

.samples-list h4 {
  margin: 0 0 12px 0;
  color: var(--color-text-secondary, #cbd5e1);
  font-size: 0.95rem;
}

.samples-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 360px;
  overflow-y: auto;
}

.sample-item {
  background: var(--color-bg-secondary, #111827);
  border: 1px solid var(--color-border, #334155);
  border-radius: 6px;
  padding: 12px;
  font-size: 0.85rem;
}

.sample-item pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-secondary, #cbd5e1);
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  line-height: 1.4;
}

.preview-merge-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary, #cbd5e1);
  font-size: 0.9rem;
  cursor: pointer;
}

.stage-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.connections-next-hint {
  margin-top: 12px;
  color: var(--color-text-muted, #94a3b8);
  font-size: 0.9rem;
  text-align: center;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

.form-card {
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  background: var(--color-bg-secondary, #1f2937);
  padding: 14px;
}

.form-card h3 {
  margin: 0 0 12px;
  color: var(--color-text-primary, #e2e8f0);
  font-size: 1rem;
  font-weight: 600;
}

/* Wizard (Mapping / Preview screens) */
.wizard-shell {
  min-height: 100%;
  background: #0f172a;
  color: #f8fafc;
  border: none !important;
  border-radius: 0;
  display: grid;
  grid-template-columns: 1fr;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  padding: 0 !important;
}

.wizard-main {
  padding: 18px;
  display: grid;
  gap: 14px;
  background: radial-gradient(circle at 30% 0%, rgba(6, 182, 212, 0.07), transparent 36%), #0f172a;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
}

.wizard-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.wizard-header p {
  margin: 4px 0 0;
  color: #94a3b8;
}

.wizard-connections {
  display: flex;
  gap: 10px;
  align-items: center;
}

.wizard-conn-card {
  min-width: 170px;
  padding: 10px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827, #1f2937);
  display: grid;
  gap: 2px;
}

.wizard-conn-card-header {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.wizard-conn-logo {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.wizard-conn-glyph {
  font-size: 0.85rem;
}

.wizard-conn-card small {
  color: #22c55e;
}

.wizard-conn-card span {
  color: #94a3b8;
  font-size: 0.82rem;
}

.wizard-conn-card.target small {
  color: #06b6d4;
}

.wizard-conn-arrow {
  color: #94a3b8;
}

.wizard-upper-grid {
  display: grid;
  grid-template-columns: minmax(180px, 0.6fr) minmax(0, 2.8fr) minmax(180px, 0.6fr);
  gap: 10px;
  align-items: stretch;
}

.wizard-upper-grid > .wizard-card,
.wizard-lower-grid > .wizard-card {
  min-width: 0;
}

.wizard-card {
  border: 1px solid #334155;
  border-radius: 12px;
  background: linear-gradient(180deg, #111827, #1f2937);
  padding: 10px;
  min-height: 100%;
}

.wizard-card h3 {
  margin: 0;
  font-size: 0.95rem;
}

.wizard-search,
.wizard-select {
  width: 90%;
  margin-top: 8px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e2e8f0;
  padding: 7px 8px;
  font-size: 0.82rem;
}

.wizard-field-list {
  display: grid;
  gap: 4px;
  margin: 10px 0;
}

.wizard-field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 5px 4px;
}

.wizard-field-name {
  color: #e2e8f0;
  font-size: 0.83rem;
}

.wizard-type-pill {
  font-size: 0.72rem;
  border-radius: 999px;
  padding: 2px 8px;
  border: 1px solid #334155;
}

.wizard-type-pill.type-string { color: #a78bfa; }
.wizard-type-pill.type-object { color: #f59e0b; }
.wizard-type-pill.type-date   { color: #06b6d4; }
.wizard-type-pill.type-array  { color: #eab308; }
.wizard-type-pill.type-objectid { color: #60a5fa; }
.wizard-type-pill.type-number { color: #a78bfa; }
.wizard-type-pill.type-boolean { color: #06b6d4; }
.wizard-type-pill.type-unknown { color: #94a3b8; }

.wizard-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.wizard-table-header > div {
  display: flex;
  gap: 8px;
}

.wizard-table-wrap {
  overflow-x: auto;
  overflow-y: visible;
  max-width: 100%;
  max-height: none;
}

.wizard-table {
  margin-top: 8px;
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
}

.wizard-table th,
.wizard-table td {
  border-bottom: 1px solid #334155;
  padding: 6px;
  font-size: 0.76rem;
  color: #e2e8f0;
  vertical-align: middle;
  white-space: normal;
}

.wizard-table th {
  color: #94a3b8;
  text-transform: uppercase;
  font-size: 0.68rem;
  letter-spacing: 0.04em;
}

.wizard-table th:nth-child(1),
.wizard-table td:nth-child(1) { width: 34px; }
.wizard-table th:nth-child(2),
.wizard-table td:nth-child(2) { width: 120px; }
.wizard-table th:nth-child(3),
.wizard-table td:nth-child(3) { width: 110px; }
.wizard-table th:nth-child(4),
.wizard-table td:nth-child(4) { width: 92px; white-space: nowrap; }
.wizard-table th:nth-child(5),
.wizard-table td:nth-child(5) { width: 95px; }
.wizard-table th:nth-child(6),
.wizard-table td:nth-child(6) { width: 70px; }
.wizard-table th:nth-child(7),
.wizard-table td:nth-child(7) { width: 75px; }
.wizard-table th:nth-child(8),
.wizard-table td:nth-child(8) { width: 92px; white-space: nowrap; }

.mapping-table-panel { min-width: 0; }

.wizard-table .wizard-select {
  margin-top: 0;
  font-size: 0.75rem;
  padding: 5px 6px;
}

.wizard-inline-code {
  display: inline-block;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.72rem;
  color: #cbd5e1;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 5px 7px;
}

.wizard-remove-button {
  border: 1px solid #334155;
  background: #0f172a;
  color: #cbd5e1;
  border-radius: 8px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.wizard-action-icon {
  border: 1px solid #334155;
  background: #0f172a;
  color: #67e8f9;
  border-radius: 8px;
  width: 28px;
  height: 28px;
  margin-right: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.wizard-row-actions {
  display: flex;
  align-items: center;
}

.wizard-remove-button:disabled,
.wizard-action-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.wizard-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.72);
  display: grid;
  place-items: center;
  z-index: 60;
}

.wizard-modal {
  width: min(560px, calc(100vw - 32px));
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 16px;
  background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
  display: grid;
  gap: 10px;
}

.wizard-modal h3 { margin: 0; }
.wizard-modal p  { margin: 0; color: #94a3b8; }

.wizard-modal-label {
  font-size: 0.8rem;
  color: #cbd5e1;
}

.wizard-rule-mode-toggle {
  display: grid;
  gap: 8px;
  margin-bottom: 4px;
}

.wizard-rule-mode-toggle label {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  font-size: 0.86rem;
  color: #e2e8f0;
}

.wizard-rule-mode-toggle-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #e2e8f0;
  font-size: 0.86rem;
}

.wizard-modal-error {
  color: #f87171 !important;
  font-size: 0.82rem;
}

.wizard-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

.wizard-lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  margin-top: 20px;
}

.validation-panel {
  grid-column: 1 / -1;
  margin-top: 20px;
}

.wizard-code {
  margin: 8px 0 0;
  min-height: 230px;
  max-height: 260px;
  overflow: auto;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.75rem;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 8px;
  background: #0b1220;
}

.wizard-code .ln {
  color: #64748b;
  display: inline-block;
  width: 22px;
  margin-right: 8px;
  text-align: right;
  user-select: none;
}

.wizard-checklist {
  margin: 8px 0 0;
  padding-left: 18px;
  color: #cbd5e1;
  display: grid;
  gap: 8px;
  font-size: 0.85rem;
}

.wizard-status {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 700;
}

.wizard-status.valid {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.wizard-status.optional {
  background: rgba(6, 182, 212, 0.16);
  color: #67e8f9;
}

.wizard-status.warn {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.wizard-actions {
  border-top: 1px solid #334155;
  margin-top: 50px;
  padding-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wizard-actions > div {
  display: flex;
  gap: 8px;
}

.wizard-primary {
  border-radius: 9px;
  border: 1px solid rgba(34, 197, 94, 0.5);
  background: #22c55e;
  color: #052e16;
  padding: 8px 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.wizard-primary:hover:not(:disabled) {
  background: #16a34a;
}

.wizard-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.wizard-secondary {
  border-radius: 9px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #d1d5db;
  padding: 8px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.wizard-secondary:hover:not(:disabled) {
  background: #1f2937;
}

.wizard-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Preview + Jobs parity (restored from original layout) */
.card {
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 18px;
}

.primary-button.secondary {
  background: #111827;
  border: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.85rem;
  padding: 8px 14px;
  margin-top: 6px;
}

.primary-button.secondary:hover:not(:disabled) {
  background: #1f2937;
}

.preview-panel {
  overflow: hidden;
}

.preview-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 18px;
}

.preview-header-enterprise {
  padding: 14px 16px;
  border: 1px solid #334155;
  border-radius: 16px;
  background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
}

.preview-header h2,
.preview-card h3 {
  margin: 0;
}

.preview-header p {
  margin: 6px 0 0;
  color: #94a3b8;
}

.preview-stage {
  display: grid;
  gap: 18px;
  padding: 18px;
  border: 1px solid #334155;
  border-radius: 20px;
  background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
}

.preview-flow {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 18px;
  align-items: center;
}

.preview-actions {
  display: grid;
  gap: 10px;
  margin-top: 30px;
}

.preview-actions h3 {
  margin: 0;
}

.preview-actions p {
  margin: 0;
  color: #94a3b8;
}

.preview-warning-text {
  color: #fbbf24;
  font-size: 0.82rem;
}

.preview-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: end;
}

.preview-actions-row label {
  min-width: 220px;
  flex: 1;
}

.preview-merge-toggle {
  min-width: 240px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #cbd5e1;
}

.preview-card {
  position: relative;
  min-height: 100%;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid #334155;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.35);
}

.preview-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.4), rgba(34, 197, 94, 0.22));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.preview-card-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 9999px;
  background: rgba(6, 182, 212, 0.12);
  color: #67e8f9;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.preview-card-badge.success {
  background: rgba(34, 197, 94, 0.12);
  color: #4ade80;
}

.preview-field-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.preview-field-row {
  display: grid;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #334155;
  background: #111827;
}

.preview-field-row.source-row {
  background: #0f172a;
}

.preview-field-row.mapped-row {
  border-color: rgba(6, 182, 212, 0.3);
  background: rgba(8, 47, 73, 0.48);
}

.preview-field-row.manual-row {
  border-color: rgba(245, 158, 11, 0.34);
  background: rgba(69, 39, 9, 0.55);
}

.preview-field-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.preview-field-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #f8fafc;
  word-break: break-word;
}

.preview-field-value {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.84rem;
  line-height: 1.45;
  color: #cbd5e1;
  word-break: break-word;
}

.preview-field-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.preview-field-tag.mapped {
  background: rgba(6, 182, 212, 0.12);
  color: #67e8f9;
}

.preview-field-tag.manual {
  background: rgba(245, 158, 11, 0.16);
  color: #fbbf24;
}

.preview-footer-actions {
  margin-top: 12px;
  padding-top: 12px;
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

.job-rerun-button,
.job-delete-button {
  margin-top: 0;
  padding: 7px 10px;
  font-size: 0.8rem;
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

.job-status.pending,
.job-status.loading_source,
.job-status.mapping_fields,
.job-status.inserting_documents {
  background: rgba(37, 99, 235, 0.12);
  color: #93c5fd;
}

.job-status.done {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.job-status.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.job-progress-track {
  height: 8px;
  border-radius: 9999px;
  background: #1f2937;
  overflow: hidden;
}

.job-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #0ea5e9 100%);
  transition: width 0.3s ease;
}

.job-progress-text {
  margin: 0;
  font-size: 0.82rem;
  color: #94a3b8;
}

.job-steps {
  display: grid;
  gap: 8px;
}

.job-step {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #334155;
  background: #0f172a;
}

.job-step.active {
  border-color: rgba(37, 99, 235, 0.4);
  background: rgba(30, 58, 138, 0.35);
}

.job-step.done {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(6, 78, 59, 0.35);
}

.job-step-label {
  font-size: 0.84rem;
  font-weight: 600;
  color: #e2e8f0;
}

.job-step-done {
  font-size: 0.74rem;
  color: #34d399;
  font-weight: 700;
  text-transform: uppercase;
}

.job-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #93c5fd;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin-job 0.8s linear infinite;
}

@keyframes spin-job {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.job-result p {
  margin: 0;
  font-size: 0.84rem;
  color: #cbd5e1;
}

.job-error {
  color: #f87171 !important;
}

.job-hint.warning {
  color: #fbbf24 !important;
  font-weight: 600;
}

.jobs-pagination {
  margin-top: 20px;
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

/* Templates */
.templates-card {
  display: grid;
  gap: 10px;
}

.templates-list {
  display: grid;
  gap: 10px;
}

.template-item {
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  background: var(--color-bg-tertiary, #0f172a);
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.template-item p {
  margin: 4px 0;
  color: var(--color-text-secondary, #cbd5e1);
}

.template-item small {
  color: var(--color-text-muted, #94a3b8);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-muted, #94a3b8);
}

.text-muted {
  color: var(--color-text-muted, #94a3b8);
}

/* Responsive */
@media (max-width: 900px) {
  .global-shell {
    grid-template-columns: 1fr;
  }

  .global-sidebar {
    border-right: none;
    border-bottom: 1px solid var(--color-border, #334155);
    flex-direction: row;
    padding: 10px;
    gap: 10px;
  }

  .global-nav {
    flex-direction: row;
    overflow-x: auto;
  }

  .migration-flow-header {
    flex-direction: column;
    align-items: stretch;
  }

  .engines-path-row {
    grid-template-columns: 1fr;
  }

  .engine-path-arrow {
    transform: rotate(90deg);
  }

  .engines-grid,
  .engine-actions {
    grid-template-columns: 1fr;
  }

  .dashboard-metrics {
    grid-template-columns: 1fr;
  }

  .dashboard-middle-grid,
  .dashboard-bottom-grid {
    grid-template-columns: 1fr;
  }

  .wizard-upper-grid,
  .wizard-lower-grid {
    grid-template-columns: 1fr;
  }

  .wizard-actions {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }

  .wizard-actions > div {
    width: 100%;
  }
}
</style>
