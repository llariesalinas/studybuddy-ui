import { computed } from 'vue'

const CATEGORY_MAP = {
  elementary: 'Elementary',
  jhs: 'JHS',
  shs: 'SHS',
  college: 'College'
}

const GENERAL_GROUPS = new Set([
  'general',
  'general education',
  'general subjects',
  'core',
  'common',
  'all levels'
])

export function useSubjectCatalog({
  subjects,
  courses,
  educationLevel,
  selectedCourseCode,
  subjectSearch,
  activeCategory,
  selectedSubjectCodes,
  draftSubjectCodes,
  isSubjectModalOpen
}) {
  const hasSubjectsForCurrentLevel = computed(() => {
    const activeLevelCategory = CATEGORY_MAP[educationLevel.value]

    if (!activeLevelCategory) {
      return false
    }

    return subjects.value.some(subject => normalizeCategory(subject.category) === activeLevelCategory)
  })

  const levelScopedSubjects = computed(() => {
    const activeLevelCategory = CATEGORY_MAP[educationLevel.value]

    return subjects.value.filter(subject => {
      if (isGeneralSubject(subject)) {
        return true
      }

      if (!activeLevelCategory || !hasSubjectsForCurrentLevel.value) {
        return true
      }

      return normalizeCategory(subject.category) === activeLevelCategory
    })
  })

  const prioritizedSubjects = computed(() =>
    [...levelScopedSubjects.value].sort((left, right) => {
      const priorityDelta = getSubjectPriorityScore(right) - getSubjectPriorityScore(left)

      if (priorityDelta !== 0) {
        return priorityDelta
      }

      const leftGroup = getSubjectGroup(left)
      const rightGroup = getSubjectGroup(right)
      const groupDelta = leftGroup.localeCompare(rightGroup)

      if (groupDelta !== 0) {
        return groupDelta
      }

      return left.subject_name.localeCompare(right.subject_name)
    })
  )

  const recommendedSubjects = computed(() =>
    prioritizedSubjects.value.filter(subject => getSubjectPriorityScore(subject) > 0)
  )

  const availableCategories = computed(() => {
    const groupScores = new Map()

    levelScopedSubjects.value.forEach(subject => {
      const group = getSubjectGroup(subject)
      const score = Math.max(groupScores.get(group) || 0, getSubjectPriorityScore(subject))
      groupScores.set(group, score)
    })

    const groups = [...groupScores.entries()]
      .sort((left, right) => {
        const priorityDelta = right[1] - left[1]

        if (priorityDelta !== 0) {
          return priorityDelta
        }

        return left[0].localeCompare(right[0])
      })
      .map(([group]) => group)

    return recommendedSubjects.value.length
      ? ['All', 'Recommended', ...groups]
      : ['All', ...groups]
  })

  const filteredSubjects = computed(() => {
    const query = subjectSearch.value.trim().toLowerCase()

    return prioritizedSubjects.value.filter(subject => {
      const group = getSubjectGroup(subject)
      const matchesCategory =
        activeCategory.value === 'All' ||
        (activeCategory.value === 'Recommended' && getSubjectPriorityScore(subject) > 0) ||
        group === activeCategory.value
      const matchesSearch =
        !query ||
        subject.subject_name.toLowerCase().includes(query) ||
        subject.subject_code.toLowerCase().includes(query) ||
        getSubjectGroup(subject).toLowerCase().includes(query)

      return matchesCategory && matchesSearch
    })
  })

  const groupedSubjectSections = computed(() => {
    if (activeCategory.value === 'Recommended') {
      return [{
        name: getRecommendedSectionLabel(),
        subjects: filteredSubjects.value
      }]
    }

    const groups = new Map()

    filteredSubjects.value.forEach(subject => {
      const group = getSubjectGroup(subject)

      if (!groups.has(group)) {
        groups.set(group, [])
      }

      groups.get(group).push(subject)
    })

    return [...groups.entries()].map(([name, groupedSubjects]) => ({
      name,
      subjects: groupedSubjects
    }))
  })

  const selectedSubjectObjects = computed(() => {
    const selectedCodes = new Set(selectedSubjectCodes.value)
    return subjects.value
      .filter(subject => selectedCodes.has(subject.subject_code))
      .sort((left, right) => {
        const priorityDelta = getSubjectPriorityScore(right) - getSubjectPriorityScore(left)

        if (priorityDelta !== 0) {
          return priorityDelta
        }

        return left.subject_name.localeCompare(right.subject_name)
      })
  })

  function normalizeCategory(category) {
    const normalized = category?.trim()
    return normalized || 'Uncategorized'
  }

  function normalizeDepartment(department) {
    const normalized = department?.trim()
    return normalized || ''
  }

  function isGeneralSubject(subject) {
    if (subject.is_general || subject.applies_to_all) {
      return true
    }

    return [subject.department, subject.category]
      .map(value => String(value || '').trim().toLowerCase())
      .some(value => GENERAL_GROUPS.has(value))
  }

  function getSubjectGroup(subject) {
    return normalizeDepartment(subject.department) || normalizeCategory(subject.category)
  }

  function getSelectedCourseTokens() {
    const selectedCourse = courses.value.find(course => course.course_code === selectedCourseCode.value)

    if (!selectedCourse) {
      return []
    }

    const label = `${selectedCourse.course_code || ''} ${selectedCourse.course_name || ''}`.toLowerCase()
    const tokens = label
      .split(/[^a-z0-9]+/)
      .filter(token => token.length >= 3)
      .filter(token => !['the', 'and', 'for', 'bachelor', 'science'].includes(token))

    if (label.includes('computer science') || label.includes('bscs')) {
      tokens.push('computer', 'computing', 'programming', 'algorithm', 'data')
    }

    if (label.includes('information technology') || label.includes('bsit')) {
      tokens.push('information', 'technology', 'network', 'web', 'programming')
    }

    if (label.includes('business') || label.includes('bsba')) {
      tokens.push('business', 'accounting', 'management', 'finance', 'marketing')
    }

    if (label.includes('stem')) {
      tokens.push('math', 'science', 'physics', 'chemistry', 'biology')
    }

    if (label.includes('abm')) {
      tokens.push('business', 'accounting', 'management', 'finance')
    }

    if (label.includes('humss')) {
      tokens.push('humanities', 'social', 'writing', 'english', 'communication')
    }

    return [...new Set(tokens)]
  }

  function getSubjectPriorityScore(subject) {
    const tokens = getSelectedCourseTokens()

    if (!tokens.length) {
      return 0
    }

    const haystack = [
      subject.subject_code,
      subject.subject_name,
      subject.department,
      subject.category,
    ].join(' ').toLowerCase()

    return tokens.reduce((score, token) => {
      if (haystack.includes(token)) {
        return score + 1
      }

      return score
    }, 0)
  }

  function getRecommendedSectionLabel() {
    const selectedCourse = courses.value.find(course => course.course_code === selectedCourseCode.value)

    if (!selectedCourse) {
      return 'Recommended'
    }

    return `Recommended for ${selectedCourse.course_code}`
  }

  function getPreferredSubjectCategory() {
    return recommendedSubjects.value.length ? 'Recommended' : 'All'
  }

  function pruneSubjectsForCurrentLevel() {
    const validCodes = new Set(levelScopedSubjects.value.map(subject => subject.subject_code))
    selectedSubjectCodes.value = selectedSubjectCodes.value.filter(code => validCodes.has(code))
  }

  function pruneDraftSubjectsForCurrentLevel() {
    const validCodes = new Set(levelScopedSubjects.value.map(subject => subject.subject_code))
    draftSubjectCodes.value = draftSubjectCodes.value.filter(code => validCodes.has(code))
  }

  function refreshSubjectFilterForAcademicContext({ preferRecommended = false } = {}) {
    if (preferRecommended || !availableCategories.value.includes(activeCategory.value)) {
      activeCategory.value = getPreferredSubjectCategory()
    }

    subjectSearch.value = ''

    if (isSubjectModalOpen?.value) {
      pruneDraftSubjectsForCurrentLevel()
    }
  }

  return {
    availableCategories,
    filteredSubjects,
    groupedSubjectSections,
    levelScopedSubjects,
    recommendedSubjects,
    selectedSubjectObjects,
    getPreferredSubjectCategory,
    getSubjectGroup,
    getSubjectPriorityScore,
    pruneDraftSubjectsForCurrentLevel,
    pruneSubjectsForCurrentLevel,
    refreshSubjectFilterForAcademicContext
  }
}
