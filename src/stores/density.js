import { ref } from 'vue'
import { defineStore } from 'pinia'

// Roles that render at 80% density. Admin stays at 100%.
const COMPACT_ROLES = new Set(['tutee', 'tutor', 'superadmin'])

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
    setDensity(COMPACT_ROLES.has(role?.toLowerCase()) ? 'compact' : 'comfortable')
  }

  return { density, setDensity, syncFromRole }
})
