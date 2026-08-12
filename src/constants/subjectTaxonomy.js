export const TAXONOMY_CATEGORIES = [
  'Mathematics & Data Sciences',
  'Natural Sciences',
  'Technology & Computer Science',
  'Business, Finance & Economics',
  'Humanities & Social Sciences',
  'Hobbies & Arts',
]

// Categories admins have added beyond the curated list above still live only as free text on
// `Subjects.category` (no dedicated taxonomy table). This derives the full pickable list by
// unioning the curated floor with whatever distinct categories already exist in the catalog, so
// a category added once shows up everywhere that calls this — without a backend migration.
export function deriveCategoryOptions(catalogSubjects = []) {
  const extra = new Set()
  for (const subject of catalogSubjects) {
    const value = subject?.category?.trim()
    if (value && !TAXONOMY_CATEGORIES.includes(value)) extra.add(value)
  }
  return [...TAXONOMY_CATEGORIES, ...[...extra].sort()]
}
