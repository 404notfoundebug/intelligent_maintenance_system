import request from './request'

export function getRepairCases(params) {
  return request.get('/api/cases', { params })
}

export function createRepairCase(data) {
  return request.post('/api/cases', data)
}

export function auditRepairCase(id, data) {
  return request.post(`/api/cases/${id}/audit`, data)
}
