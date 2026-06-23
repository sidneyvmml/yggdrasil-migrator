/**
 * Composable para gerenciar tema (dark/light)
 * Responsabilidade: persistência de tema, aplicação de CSS variables
 */
import { ref, computed, watch } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'yggdrasil-theme'
const DEFAULT_THEME = 'dark'

export function useTheme() {
  const currentTheme = ref<Theme>(loadThemeFromStorage())

  /**
   * Carrega tema do localStorage
   */
  function loadThemeFromStorage(): Theme {
    if (typeof localStorage === 'undefined') return DEFAULT_THEME

    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'dark' || stored === 'light') return stored

    // Verifica preferência do sistema
    if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light'
    }

    return DEFAULT_THEME
  }

  /**
   * Alterna entre temas
   */
  const toggleTheme = (): void => {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  }

  /**
   * Define tema específico
   */
  const setTheme = (theme: Theme): void => {
    currentTheme.value = theme
  }

  /**
   * Aplica tema ao DOM
   */
  const applyTheme = (theme: Theme): void => {
    if (typeof document === 'undefined') return

    const html = document.documentElement
    html.setAttribute('data-theme', theme)
    html.style.colorScheme = theme

    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, theme)
    }
  }

  /**
   * Observa mudanças de tema e aplica ao DOM
   */
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  // Aplica tema inicial ao montar
  applyTheme(currentTheme.value)

  const isDark = computed(() => currentTheme.value === 'dark')
  const isLight = computed(() => currentTheme.value === 'light')

  return {
    currentTheme,
    isDark,
    isLight,
    toggleTheme,
    setTheme,
  }
}
