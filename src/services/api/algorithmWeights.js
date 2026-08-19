// SuperAdmin-only recommender weight settings. Unlike the algorithm demo tools,
// getting and saving weights is NOT gated on ALGORITHM_DEMO_TOOLS_ENABLED - a
// control an admin cannot reach in a normal deployment would not make the
// algorithm tunable. The preview below is gated, because it renders real tutee
// names; `preview_enabled` on the settings response says whether it is on.
// See docs/plans/2026-08-19-dynamic-algorithm-weights.md.
import api from './api'

export const getAlgorithmWeights = () => api.get('admin/algorithm-weights/')

// groups is { [group]: { [key]: rawValue } }. Values are stored as sent and
// normalised server-side at score time, so partial updates are safe.
export const updateAlgorithmWeights = (groups) =>
  api.patch('admin/algorithm-weights/', { groups })

// Scores one tutee against uncommitted weights and writes nothing, so the admin
// can see the consequence before saving.
export const previewAlgorithmWeights = (tuteeId, groups = null) =>
  api.post('admin/algorithm-weights/preview/', {
    tutee_id: tuteeId,
    groups: groups || undefined
  })
