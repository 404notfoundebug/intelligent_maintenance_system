import request from './request'

export function getRepairCases(params) {
  return request.get('/api/cases', { params })
}

export function getRepairCaseDetail(id) {
  return request.get(`/api/cases/${id}`)
}

export function createRepairCase(data) {
  return request.post('/api/cases', data)
}

export function updateRepairCase(id, data) {
  return request.put(`/api/cases/${id}`, data)
}

export function auditRepairCase(id, data) {
  return request.post(`/api/cases/${id}/audit`, data)
}

export function getCaseAuditRecords(id) {
  return request.get(`/api/cases/${id}/audit-records`)
}

export function deleteRepairCase(id) {
  return request.delete(`/api/cases/${id}`)
}
