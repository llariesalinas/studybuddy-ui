import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light')

  function setTheme(value) {
    if (value !== 'light' && value !== 'dark') return

    theme.value = value
    document.documentElement.setAttribute('data-sb-theme', value)
    localStorage.setItem('sb-theme', value)
  }

  function toggleTheme() {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  function initTheme() {
    const saved = localStorage.getItem('sb-theme')
    setTheme(saved === 'dark' ? 'dark' : 'light')
  }

  return { theme, setTheme, toggleTheme, initTheme }
})
