import { computed } from 'vue'

export function useSubjectCatalog({
  subjects,
  subjectSearch,
  activeCategory,
  selectedSubjectCodes,
  isSubjectModalOpen,
}) {
  const levelScopedSubjects = computed(() => subjects.value)
  const availableCategories = computed(() => [
    'All',
    ...new Set(subjects.value.map((subject) => normalizeCategory(subject.category)).sort()),
  ])
  const filteredSubjects = computed(() => {
    const query = subjectSearch.value.trim().toLowerCase()
    return subjects.value.filter((subject) => {
      const category = normalizeCategory(subject.category)
      return (
        (activeCategory.value === 'All' || category === activeCategory.value)
        && (!query || subject.subject_name.toLowerCase().includes(query) || category.toLowerCase().includes(query))
      )
    })
  })
  const groupedSubjectSections = computed(() => availableCategories.value.slice(1).map((name) => ({
    name,
    subjects: filteredSubjects.value.filter((subject) => normalizeCategory(subject.category) === name),
  })).filter((section) => section.subjects.length))
  const selectedSubjectObjects = computed(() => {
    const selectedCodes = new Set(selectedSubjectCodes.value)
    return subjects.value.filter((subject) => selectedCodes.has(subject.subject_code))
  })
  function normalizeCategory(category) { return category?.trim() || 'Uncategorized' }
  function getSubjectGroup(subject) { return normalizeCategory(subject.category) }
  function getPreferredSubjectCategory() { return 'All' }
  function pruneSubjectsForCurrentLevel() {}
  function pruneDraftSubjectsForCurrentLevel() {}
  function refreshSubjectFilterForAcademicContext() {
    if (!availableCategories.value.includes(activeCategory.value)) activeCategory.value = 'All'
    subjectSearch.value = ''
    if (isSubjectModalOpen?.value) pruneDraftSubjectsForCurrentLevel()
  }
  return { availableCategories, filteredSubjects, groupedSubjectSections, levelScopedSubjects, selectedSubjectObjects, getPreferredSubjectCategory, getSubjectGroup, pruneDraftSubjectsForCurrentLevel, pruneSubjectsForCurrentLevel, refreshSubjectFilterForAcademicContext }
}
