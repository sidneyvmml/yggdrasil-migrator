/**
 * Composable para gerenciar templates
 * Responsabilidade: CRUD de templates, aplicação de templates
 */
import { ref, reactive } from 'vue'
import { apiClient } from '@/services/api'
import { TemplateItem } from '@/types/migration'

export function useTemplates() {
  const templates = ref<TemplateItem[]>([])
  const templatesLoading = ref(false)
  const templatesSaving = ref(false)
  const templatesFeedback = ref('')
  const templatesFeedbackType = ref<'success' | 'error'>('success')
  const templatesDeletingId = ref('')

  const templateForm = reactive({
    name: '',
    description: '',
  })

  /**
   * Carrega lista de templates
   */
  const loadTemplates = async (): Promise<void> => {
    templatesLoading.value = true
    try {
      const response = await apiClient.getTemplates()
      templates.value = response.data.templates || []
    } catch (error) {
      console.error('Erro ao carregar templates:', error)
      templates.value = []
    } finally {
      templatesLoading.value = false
    }
  }

  /**
   * Salva novo template
   */
  const saveTemplate = async (config: any): Promise<void> => {
    if (!templateForm.name.trim()) {
      templatesFeedback.value = 'Nome do template é obrigatório'
      templatesFeedbackType.value = 'error'
      return
    }

    templatesSaving.value = true
    try {
      const response = await apiClient.createTemplate({
        name: templateForm.name,
        description: templateForm.description,
        config,
      })

      templates.value.push(response.data.template)
      templateForm.name = ''
      templateForm.description = ''
      templatesFeedback.value = 'Template salvo com sucesso!'
      templatesFeedbackType.value = 'success'

      setTimeout(() => {
        templatesFeedback.value = ''
      }, 3000)
    } catch (error) {
      templatesFeedback.value = 'Erro ao salvar template'
      templatesFeedbackType.value = 'error'
      console.error('Erro ao salvar template:', error)
    } finally {
      templatesSaving.value = false
    }
  }

  /**
   * Deleta template
   */
  const deleteTemplate = async (templateId: string): Promise<void> => {
    templatesDeletingId.value = templateId
    try {
      await apiClient.deleteTemplate(templateId)
      templates.value = templates.value.filter((t) => t.templateId !== templateId)
    } catch (error) {
      console.error('Erro ao deletar template:', error)
    } finally {
      templatesDeletingId.value = ''
    }
  }

  /**
   * Aplica template aos campos atuais
   */
  const applyTemplate = async (template: TemplateItem): Promise<any> => {
    try {
      const response = await apiClient.applyTemplate(template.templateId)
      return response.data.config
    } catch (error) {
      console.error('Erro ao aplicar template:', error)
      return null
    }
  }

  /**
   * Formata data de template
   */
  const formatTemplateDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return {
    templates,
    templatesLoading,
    templatesSaving,
    templatesFeedback,
    templatesFeedbackType,
    templatesDeletingId,
    templateForm,
    loadTemplates,
    saveTemplate,
    deleteTemplate,
    applyTemplate,
    formatTemplateDate,
  }
}
