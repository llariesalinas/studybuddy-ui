import { describe, expect, it } from 'vitest'
import { categoryClass, searchSubjects, subjectCategories } from './subjectPicker.shared'

const subjects = [
  {
    subject_code: 'calculus-2',
    subject_name: 'Calculus II',
    category: 'Mathematics & Data Sciences',
    keywords: 'derivatives, integrals, limits',
  },
  {
    subject_code: 'physics-1',
    subject_name: 'Physics I',
    category: 'Natural Sciences',
    keywords: 'mechanics, calculus based',
  },
  {
    subject_code: 'programming-fundamentals',
    subject_name: 'Programming Fundamentals',
    category: 'Technology & Computer Science',
    keywords: 'coding, python, java',
  },
  {
    subject_code: 'no-keywords',
    subject_name: 'Keywordless Subject',
    category: 'Hobbies & Arts',
    keywords: null,
  },
]

describe('searchSubjects', () => {
  it('returns an empty list for an empty or whitespace query', () => {
    expect(searchSubjects(subjects, '')).toEqual([])
    expect(searchSubjects(subjects, '   ')).toEqual([])
  })

  it('matches by subject name, case-insensitively', () => {
    const results = searchSubjects(subjects, 'CALCULUS')
    expect(results.map((subject) => subject.subject_code)).toContain('calculus-2')
  })

  it('matches by category name', () => {
    const results = searchSubjects(subjects, 'natural sci')
    expect(results.map((subject) => subject.subject_code)).toEqual(['physics-1'])
  })

  it('matches by keyword and flags keyword-only matches', () => {
    const results = searchSubjects(subjects, 'coding')
    expect(results).toHaveLength(1)
    expect(results[0].subject_code).toBe('programming-fundamentals')
    expect(results[0].matchedViaKeyword).toBe(true)
  })

  it('does not leak internal matching fields onto results', () => {
    const results = searchSubjects(subjects, 'calculus')
    expect(results[0]).not.toHaveProperty('isMatch')
  })

  it('does not flag matchedViaKeyword when the name also matches', () => {
    const results = searchSubjects(subjects, 'calculus')
    const calculus = results.find((subject) => subject.subject_code === 'calculus-2')
    const physics = results.find((subject) => subject.subject_code === 'physics-1')
    expect(calculus.matchedViaKeyword).toBe(false)
    expect(physics.matchedViaKeyword).toBe(true)
  })

  it('tolerates subjects with missing keywords or category', () => {
    const sparse = [{ subject_code: 'x', subject_name: 'X Marks', category: null, keywords: null }]
    expect(searchSubjects(sparse, 'marks')).toHaveLength(1)
    expect(searchSubjects(sparse, 'zzz')).toHaveLength(0)
  })
})

describe('categoryClass', () => {
  it('maps each taxonomy category to exactly one accent class', () => {
    const classes = categoryClass('Technology & Computer Science')
    expect(classes['cat-tech']).toBe(true)
    expect(Object.values(classes).filter(Boolean)).toHaveLength(1)
  })

  it('activates no accent class for unknown categories', () => {
    expect(Object.values(categoryClass('Unknown')).some(Boolean)).toBe(false)
  })
})

describe('subjectCategories', () => {
  it('returns unique categories in order of first appearance, skipping blanks', () => {
    const withBlank = [...subjects, { subject_code: 'y', subject_name: 'Y', category: '' }]
    expect(subjectCategories(withBlank)).toEqual([
      'Mathematics & Data Sciences',
      'Natural Sciences',
      'Technology & Computer Science',
      'Hobbies & Arts',
    ])
  })
})
