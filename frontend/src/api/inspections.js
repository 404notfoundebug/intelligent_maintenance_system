import request from './request'

export function getInspectionOrders(params) {
  return request.get('/api/inspections/orders', { params })
}

export function getInspectionOrder(id) {
  return request.get(`/api/inspections/orders/${id}`)
}

export function createInspectionOrder(data) {
  return request.post('/api/inspections/orders', data)
}

export function startInspectionOrder(id) {
  return request.put(`/api/inspections/orders/${id}/start`)
}

export function completeInspectionOrder(id) {
  return request.put(`/api/inspections/orders/${id}/complete`)
}

export function updateInspectionStep(orderId, stepId, data) {
  return request.put(`/api/inspections/orders/${orderId}/steps/${stepId}`, data)
}

export function uploadInspectionStepPhoto(orderId, stepId, data) {
  return request.post(`/api/inspections/orders/${orderId}/steps/${stepId}/photo`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
