// Staff-only recommendation algorithm demo tool. The backend endpoints 403 unless
// ALGORITHM_DEMO_TOOLS_ENABLED is set, so these are inert outside dev/demo environments.
// See docs/specs/2026-07-04-superadmin-algorithm-demo-design.md.
import api from './api'

export const searchAlgorithmDemoTutees = (query = '', institutionId = null) =>
  api.get('dev/algorithm-demo/tutees/', {
    params: { q: query, institution_id: institutionId || undefined }
  })

export const getAlgorithmDemoRecommendation = (tuteeId, institutionId = null) =>
  api.get('dev/algorithm-demo/recommend/', {
    params: { tutee_id: tuteeId, institution_id: institutionId || undefined }
  })

// What-if re-scoring: the overrides are applied to the rating matrix in memory and
// never written, so the panel can retune a rating and watch the ranking respond
// without the experiment persisting. Same row shape as getAlgorithmDemoRecommendation.
export const getAlgorithmDemoWhatIf = (tuteeId, institutionId = null, overrides = []) =>
  api.post('dev/algorithm-demo/recommend-whatif/', {
    tutee_id: tuteeId,
    institution_id: institutionId || undefined,
    overrides
  })

export const updateAlgorithmDemoRating = (studentId, tutorId, ratingScore) =>
  api.patch('dev/algorithm-demo/rating/', {
    student_id: studentId,
    tutor_id: tutorId,
    rating_score: ratingScore
  })
