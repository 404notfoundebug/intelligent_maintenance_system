import request from './request'

export function getFaultReports(params) {
  return request.get('/api/faults', { params })
}

export function createFaultReport(data) {
  return request.post('/api/faults', data)
}

export function uploadFaultImage(faultId, data) {
  return request.post(`/api/faults/${faultId}/images`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function analyzeFaultImage(faultId, imageId) {
  return request.post(`/api/faults/${faultId}/images/${imageId}/analyze`)
}

export function generateFaultRepairAdvice(faultId, params) {
  return request.post(`/api/faults/${faultId}/repair-advice`, null, { params })
}
