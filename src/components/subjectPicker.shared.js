// Shared subject search/browse helpers for the subject picker components
// (SubjectTaxonomyPicker, SubjectPickerModal). Pure functions, no reactivity.

/**
 * A subject the user proposed that an admin hasn't reviewed yet. Mirrors
 * Subjects.STATUS_CHOICES on the backend.
 */
export const PENDING_STATUS = 'pending'

export const isPendingSubject = (subject) => subject?.status === PENDING_STATUS

/**
 * Filter subjects by a free-text query against name, category, keywords, and
 * description. Returns matches annotated with `matchedViaHint` when only the
 * keywords or description matched (used to render the "via ..." badge).
 *
 * Results are partitioned into two tiers - direct name/category matches first,
 * hint matches after - so broadening the match to descriptions cannot bury the
 * subjects the query names outright. Catalog order is preserved within a tier.
 */
export function searchSubjects(subjects, query) {
  const normalized = String(query || '')
    .trim()
    .toLowerCase()
  if (!normalized) return []

  const direct = []
  const hinted = []

  subjects.forEach((subject) => {
    const nameMatch = subject.subject_name?.toLowerCase().includes(normalized) || false
    const categoryMatch = subject.category?.toLowerCase().includes(normalized) || false
    const keywordMatch = subject.keywords?.toLowerCase().includes(normalized) || false
    const descriptionMatch = subject.description?.toLowerCase().includes(normalized) || false
    if (!nameMatch && !categoryMatch && !keywordMatch && !descriptionMatch) return

    const isDirect = nameMatch || categoryMatch
    ;(isDirect ? direct : hinted).push({ ...subject, matchedViaHint: !isDirect })
  })

  return [...direct, ...hinted]
}

/**
 * Unique, non-empty categories in order of first appearance.
 */
export function subjectCategories(subjects) {
  return [...new Set(subjects.map((subject) => subject.category).filter(Boolean))]
}

/**
 * Splits `text` into plain/matched segments around the (case-insensitive) first occurrence of
 * `query`, so a template can bold the matched span without v-html. Falls through to a single
 * unmatched segment when the query is empty or the text doesn't contain it.
 */
export function highlightSegments(text, query) {
  const normalizedQuery = String(query || '').trim().toLowerCase()
  if (!normalizedQuery) return [{ text, match: false }]

  const index = text.toLowerCase().indexOf(normalizedQuery)
  if (index === -1) return [{ text, match: false }]

  const end = index + normalizedQuery.length
  return [
    { text: text.slice(0, index), match: false },
    { text: text.slice(index, end), match: true },
    { text: text.slice(end), match: false },
  ].filter((segment) => segment.text)
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
