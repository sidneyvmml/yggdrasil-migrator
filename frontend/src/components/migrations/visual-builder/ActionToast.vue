<template>
  <transition name="toast-fade">
    <div v-if="visible" class="action-toast" role="status" aria-live="polite">
      {{ message }}
    </div>
  </transition>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  message: string
}>()
</script>

<style scoped>
.action-toast {
  position: fixed;
  right: 22px;
  bottom: 22px;
  z-index: 70;
  border: 1px solid rgba(34, 197, 94, 0.45);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.96);
  color: #d4f9e2;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 12px 34px rgba(0, 0, 0, 0.38);
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
