<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import AlgorithmDemoRankedList from '@/components/algorithm-demo/AlgorithmDemoRankedList.vue'
import AlgorithmDemoPairPicker from '@/components/algorithm-demo/AlgorithmDemoPairPicker.vue'
import { searchAlgorithmDemoTutees } from '@/services/api/algorithmDemo'
import { useSuperAdminStore } from '@/stores/superadmin'

const TABS = [
  { key: 'ranked', label: 'Ranked List' },
  { key: 'pair', label: 'Compare Pair' }
]

const superAdminStore = useSuperAdminStore()

const activeTab = ref('ranked')
const selectedInstitutionId = ref('')
const tutees = ref([])
const loading = ref(true)
const disabledMessage = ref('')

const institutionOptions = computed(() => [
  { value: '', label: 'All institutions' },
  ...superAdminStore.institutions.map((institution) => ({
    value: institution.id,
    label: institution.institution_name
  }))
])

async function loadTutees() {
  try {
    const { data } = await searchAlgorithmDemoTutees('', selectedInstitutionId.value || null)
    tutees.value = data.tutees
  } catch (err) {
    disabledMessage.value =
      err.response?.status === 403
        ? 'Algorithm demo tools are disabled on this backend.'
        : 'Could not load tutees for the algorithm demo.'
  }
}

watch(selectedInstitutionId, loadTutees)

onMounted(async () => {
  await Promise.all([superAdminStore.fetchInstitutions(), loadTutees()])
  loading.value = false
})
</script>

<template>
  <div class="algorithm-demo-page">
    <p class="eyebrow">Recommender Testing</p>
    <h1>Algorithm Demo</h1>
    <p class="subtitle">
      Runs the real hybrid recommender (CBF + CF) against seeded data. Staff-only.
    </p>

    <p v-if="loading" class="empty-state">Loading…</p>
    <p v-else-if="disabledMessage" class="empty-state">{{ disabledMessage }}</p>
    <template v-else>
      <div class="toolbar">
        <div class="tab-toggle" role="tablist">
          <button
            v-for="tab in TABS"
            :key="tab.key"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.key"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="institution-filter">
          <label>Institution</label>
          <SbSelectModal
            v-model="selectedInstitutionId"
            :options="institutionOptions"
            title="Filter institution"
            placeholder="All institutions"
            searchable
            clearable
            clear-label="All institutions"
          />
        </div>
      </div>

      <div class="sb-card">
        <AlgorithmDemoRankedList
          v-if="activeTab === 'ranked'"
          :tutees="tutees"
          :institution-id="selectedInstitutionId || null"
        />
        <AlgorithmDemoPairPicker
          v-else
          :tutees="tutees"
          :institution-id="selectedInstitutionId || null"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.algorithm-demo-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  font-weight: 700;
  color: var(--sb-primary);
  margin: 0 0 4px;
}

h1 {
  font-size: 24px;
  margin: 0 0 4px;
  font-weight: 700;
}

.subtitle {
  color: var(--sb-text-muted);
  font-size: 13px;
  margin: 0 0 20px;
}

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 60px 0;
}

.toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.institution-filter {
  min-width: 220px;
}

.institution-filter label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--sb-text-muted);
  margin-bottom: 6px;
}

.tab-toggle {
  display: inline-flex;
  background: var(--sb-card-border);
  border-radius: 9999px;
  padding: 4px;
  gap: 2px;
}

.tab-toggle button {
  border: none;
  background: transparent;
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--sb-text-muted);
  cursor: pointer;
}

.tab-toggle button.active {
  background: var(--sb-dark);
  color: #fff;
}

.sb-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  padding: 20px 22px;
}
</style>
