<template>
  <div class="stepper-container">
    <div class="stepper-track">
      <div class="stepper-fill" :style="{ width: progressPercentage + '%' }"></div>
    </div>
    <div class="stepper-steps">
      <button
        v-for="(step, index) in steps"
        :key="step.key"
        :class="['stepper-step', getStepClass(index)]"
        :disabled="disabled || !isClickable(index)"
        @click="$emit('step-selected', index)"
        :title="isClickable(index) ? `Go to ${step.label}` : 'Complete previous steps to unlock'"
      >
        <span class="step-number">{{ index + 1 }}</span>
        <span class="step-label">{{ step.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TabDefinition } from '@/types'

interface Props {
  /**
   * Passos do stepper
   */
  steps: TabDefinition[]

  /**
   * Índice do passo atual (0-based)
   */
  currentStep: number

  /**
   * Desabilita interação
   */
  disabled?: boolean

  /**
   * Permite retroceder livremente (true) ou apenas avançar (false)
   */
  allowBacktrack?: boolean
}

interface Emits {
  'step-selected': [stepIndex: number]
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  allowBacktrack: false,
})

defineEmits<Emits>()

/**
 * Percentual de progresso (0-100)
 */
const progressPercentage = computed(() => {
  if (props.steps.length <= 1) return 0
  return (props.currentStep / (props.steps.length - 1)) * 100
})

/**
 * Classe CSS para um step
 */
const getStepClass = (index: number): string => {
  const classes: string[] = []

  if (index < props.currentStep) {
    classes.push('completed')
  } else if (index === props.currentStep) {
    classes.push('active')
  } else {
    classes.push('pending')
  }

  return classes.join(' ')
}

/**
 * Verifica se um step pode ser clicado
 */
const isClickable = (index: number): boolean => {
  // Sempre permitir clicar no passo atual
  if (index === props.currentStep) return true

  // Se allowBacktrack, permitir clicar em qualquer passo anterior
  if (props.allowBacktrack && index < props.currentStep) return true

  // Caso contrário, não permitir
  return false
}
</script>

<style scoped>
.stepper-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stepper-track {
  position: relative;
  height: 3px;
  background: #334155;
  border-radius: 999px;
  overflow: hidden;
}

.stepper-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #10b981);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.stepper-steps {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.stepper-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
  padding: 8px 4px;
  border: none;
  background: transparent;
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.stepper-step:hover:not(:disabled) {
  background: rgba(34, 197, 94, 0.08);
  color: #cbd5e1;
}

.stepper-step:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #334155;
  font-size: 0.75rem;
  font-weight: 700;
  background: #0f172a;
}

.stepper-step.completed .step-number {
  background: #22c55e;
  border-color: #22c55e;
  color: #052e16;
}

.stepper-step.active .step-number {
  background: #06b6d4;
  border-color: #06b6d4;
  color: #082f36;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.step-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  line-height: 1.2;
}

.stepper-step.active .step-label {
  color: #dcfce7;
}

.stepper-step.completed .step-label {
  color: #86efac;
}
</style>
