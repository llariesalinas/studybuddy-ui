import api from '@/services/api/api'

export const reviewTutorProposedSubject = async (applicationId, subjectCode, status) => {
  const action = status === 'approved' ? 'approve' : 'reject'
  const { data } = await api.patch(
    `/admin/tutor-applications/${applicationId}/subjects/${subjectCode}/`,
    { action },
  )
  return data
}
