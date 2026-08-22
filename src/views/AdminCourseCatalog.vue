<template>
  <div class="admin-course-catalog p-4">
    <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
      <div><p class="text-uppercase text-muted small fw-bold mb-1">Platform catalog</p><h3 class="mb-1">Subject catalog</h3><p class="text-muted mb-0">Manage the global subject list available to every partner institution.</p></div>
      <button type="button" class="btn bg-sb-primary text-white btn-sm rounded-pill px-3 sb-btn" @click="startCreate">Add subject</button>
    </div>
    <form v-if="showForm" class="row g-3 align-items-end border rounded-4 bg-white shadow-sm p-3 mb-4" @submit.prevent="saveSubject">
      <div class="col-12 col-md-4"><label class="form-label small fw-bold">SUBJECT NAME</label><input v-model.trim="form.subject_name" class="form-control rounded-3 sb-field" required></div>
      <div class="col-12 col-md-4"><label class="form-label small fw-bold">CATEGORY</label>
        <template v-if="categoryMode === 'new'"><input v-model.trim="form.category" class="form-control rounded-3 sb-field" placeholder="New category name" required><button type="button" class="btn btn-link btn-sm px-0 mt-1" @click="useExistingCategory">Pick an existing category instead</button></template>
        <template v-else><select v-model="form.category" class="form-select rounded-3 sb-field" required @change="handleCategorySelectChange"><option value="" disabled>Select a category</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option><option :value="ADD_NEW_OPTION">+ Add new category...</option></select></template>
      </div>
      <div class="col-12 col-md-4"><label class="form-label small fw-bold">SUB-GROUP</label><input v-model.trim="form.department" class="form-control rounded-3 sb-field"></div>
      <div class="col-12"><label class="form-label small fw-bold">KEYWORDS</label><input v-model.trim="form.keywords" class="form-control rounded-3 sb-field" placeholder="Comma-separated synonyms, e.g. coding, programming, cs"></div>
      <div class="col-12"><label class="form-label small fw-bold">DESCRIPTION</label><textarea v-model.trim="form.description" class="form-control rounded-3 sb-field" rows="2" placeholder="A brief description of what this subject covers"></textarea></div>
      <div class="col-12 d-flex justify-content-end gap-2"><button type="button" class="btn btn-light rounded-pill px-3" @click="cancelForm">Cancel</button><button class="btn bg-sb-primary text-white rounded-pill px-3" :disabled="saving">{{ editingCode ? 'Save changes' : 'Add subject' }}</button></div>
    </form>
    <div class="border rounded-4 bg-white shadow-sm overflow-hidden"><div class="catalog-toolbar p-3 border-bottom"><input v-model.trim="search" class="form-control rounded-3 sb-field" placeholder="Search by name, category, or sub-group"></div>
      <div v-if="loading" class="p-4 placeholder-glow"><span v-for="index in 6" :key="index" class="placeholder col-12 rounded mb-3"></span></div>
      <div v-else-if="!filteredSubjects.length" class="p-5 text-center text-muted">No subjects match this search.</div>
      <div v-else class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Name</th><th>Category</th><th>Sub-group</th><th class="text-end">Actions</th></tr></thead><tbody><tr v-for="subject in filteredSubjects" :key="subject.subject_code"><td class="fw-semibold">{{ subject.subject_name }}</td><td>{{ subject.category }}</td><td>{{ subject.department || '—' }}</td><td class="text-end"><button type="button" class="btn btn-sm btn-light rounded-circle me-2" :aria-label="`Edit ${subject.subject_name}`" @click="startEdit(subject)">Edit</button><button type="button" class="btn btn-sm btn-light rounded-circle" :disabled="removingCode === subject.subject_code" :aria-label="`Remove ${subject.subject_name}`" @click="removeSubject(subject)">Remove</button></td></tr></tbody></table></div>
    </div>
  </div>
</template>
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useToastStore } from '@/stores/toast'
import { ADD_NEW_OPTION } from '@/constants/subjectTaxonomy'
const catalogStore = useCatalogStore(); const toastStore = useToastStore()
// The stored SubjectCategory list, so a category with no subjects yet -- one added here, or via
// the tutor-application review panel -- is still selectable. Server order is display_order, name.
const categories = computed(() => catalogStore.subjectCategories.map((category) => category.name))
// 'select' shows the dropdown; 'new' shows the free-text input for naming a category that does not
// exist yet. Same two-mode pattern the review panel uses.
const categoryMode = ref('select')
const search = ref(''); const loading = ref(false); const saving = ref(false); const removingCode = ref(null); const showForm = ref(false); const editingCode = ref(null)
const form = reactive({ subject_name: '', department: '', category: '', keywords: '', description: '' })
const filteredSubjects = computed(() => { const query = search.value.toLowerCase(); return catalogStore.courseCatalog.filter((subject) => !query || [subject.subject_name, subject.department, subject.category, subject.keywords].filter(Boolean).some((value) => String(value).toLowerCase().includes(query))) })
function resetForm() { Object.assign(form, { subject_name: '', department: '', category: '', keywords: '', description: '' }); editingCode.value = null; categoryMode.value = 'select' }
function startCreate() { resetForm(); showForm.value = true }
function startEdit(subject) { editingCode.value = subject.subject_code; categoryMode.value = 'select'; Object.assign(form, { subject_name: subject.subject_name, department: subject.department, category: subject.category, keywords: subject.keywords || '', description: subject.description || '' }); showForm.value = true }
function cancelForm() { showForm.value = false; resetForm() }
function handleCategorySelectChange() { if (form.category === ADD_NEW_OPTION) { form.category = ''; categoryMode.value = 'new' } }
function useExistingCategory() { categoryMode.value = 'select'; if (!categories.value.includes(form.category)) form.category = '' }
async function saveSubject() { saving.value = true; try { if (editingCode.value) await catalogStore.updateCatalogSubject(editingCode.value, { ...form }); else await catalogStore.addCatalogSubject({ ...form }); toastStore.push('Subject saved.', 'success'); cancelForm() } catch { toastStore.push('Failed to save subject.', 'error') } finally { saving.value = false } }
async function removeSubject(subject) { removingCode.value = subject.subject_code; try { await catalogStore.removeCatalogSubject(subject.subject_code); toastStore.push('Subject removed.', 'success') } catch { toastStore.push('Failed to remove subject.', 'error') } finally { removingCode.value = null } }
onMounted(async () => { loading.value = true; try { await Promise.all([catalogStore.fetchCourseCatalog(), catalogStore.fetchSubjectCategories()]) } catch { toastStore.push('Failed to load the global catalog.', 'error') } finally { loading.value = false } })
</script>
<style scoped>.catalog-toolbar{max-width:520px}.placeholder{display:block;height:44px}</style>
