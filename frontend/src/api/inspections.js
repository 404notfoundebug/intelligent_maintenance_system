import request from './request'

// ===== 模板 API =====

export function getInspectionTemplates(params) {
  return request.get('/api/inspections/templates', { params })
}

export function getInspectionTemplateDetail(id) {
  return request.get(`/api/inspections/templates/${id}`)
}

export function createInspectionTemplate(data) {
  return request.post('/api/inspections/templates', data)
}

export function updateInspectionTemplate(id, data) {
  return request.put(`/api/inspections/templates/${id}`, data)
}

export function deleteInspectionTemplate(id) {
  return request.delete(`/api/inspections/templates/${id}`)
}

// ===== 工单 API =====

export function getInspectionOrders(params) {
  return request.get('/api/inspections/orders', { params })
}

export function getInspectionOrderDetail(id) {
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

export function deleteInspectionOrder(id) {
  return request.delete(`/api/inspections/orders/${id}`)
}

// ===== 别名 =====

export const getInspectionOrder = getInspectionOrderDetail
export const getInspectionTemplate = getInspectionTemplateDetail
