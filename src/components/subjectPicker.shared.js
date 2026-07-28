// Shared subject search/browse helpers for the subject picker components
// (SubjectTaxonomyPicker, SubjectPickerModal). Pure functions, no reactivity.

/**
 * Filter subjects by a free-text query against name, category, and keywords.
 * Returns matches annotated with `matchedViaKeyword` when only the keywords
 * field matched (used to render the "via keyword" badge).
 */
export function searchSubjects(subjects, query) {
  const normalized = String(query || '')
    .trim()
    .toLowerCase()
  if (!normalized) return []

  return subjects.flatMap((subject) => {
    const nameMatch = subject.subject_name?.toLowerCase().includes(normalized) || false
    const categoryMatch = subject.category?.toLowerCase().includes(normalized) || false
    const keywordMatch = subject.keywords?.toLowerCase().includes(normalized) || false
    if (!nameMatch && !categoryMatch && !keywordMatch) return []
    return [{ ...subject, matchedViaKeyword: !nameMatch && !categoryMatch && keywordMatch }]
  })
}

/**
 * Unique, non-empty categories in order of first appearance.
 */
export function subjectCategories(subjects) {
  return [...new Set(subjects.map((subject) => subject.category).filter(Boolean))]
}

/**
 * Category -> scoped accent class. Both picker components define the matching
 * .cat-* rules (each sets the --cat custom property to an --sb-* accent).
 */
export function categoryClass(category) {
  return {
    'cat-math': category === 'Mathematics & Data Sciences',
    'cat-science': category === 'Natural Sciences',
    'cat-tech': category === 'Technology & Computer Science',
    'cat-business': category === 'Business, Finance & Economics',
    'cat-humanities': category === 'Humanities & Social Sciences',
    'cat-arts': category === 'Hobbies & Arts',
  }
}
