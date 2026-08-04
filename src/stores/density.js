import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useDensityStore = defineStore('density', () => {
  const density = ref('comfortable')

  function setDensity(value) {
    density.value = value === 'compact' ? 'compact' : 'comfortable'

    if (density.value === 'compact') {
      document.documentElement.setAttribute('data-sb-density', 'compact')
    } else {
      document.documentElement.removeAttribute('data-sb-density')
    }
  }

  function syncFromRole(role) {
    setDensity(role?.toLowerCase() === 'tutee' ? 'compact' : 'comfortable')
  }

  return { density, setDensity, syncFromRole }
})
