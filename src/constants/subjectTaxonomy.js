// Sentinel <option> value meaning "let me type a new one" in the Category and Sub-Group pickers.
// Shared so the admin catalog and the tutor-application review panel cannot drift apart on it.
export const ADD_NEW_OPTION = '__add_new__'

// Categories live in the SubjectCategory table and reach the frontend through the catalog store
// (`fetchSubjectCategories`). They used to be derived here by unioning a hardcoded list of six
// with the distinct categories found on catalog subjects, which meant a category with no subjects
// could not exist at all. See docs/plans/2026-08-21-subject-category-storage.md.

// Sub-Group (Subjects.department) has no table of its own — it stays a free label with
// no enforced relationship to Category. This derives the distinct sub-group values already used by
// subjects under one category, purely as a UI convenience (narrows the suggested list); it doesn't
// restrict what an admin can type via "+ Add new sub-group".
export function deriveSubgroupOptions(catalogSubjects = [], category = '') {
  const values = new Set()
  for (const subject of catalogSubjects) {
    if (subject?.category !== category) continue
    const value = subject?.department?.trim()
    if (value) values.add(value)
  }
  return [...values].sort()
}
