import request from './request'

export function getMaintenanceRecords(params) {
  return request.get('/api/maintenance/records', { params })
}

export function getMaintenanceRecord(id) {
  return request.get(`/api/maintenance/records/${id}`)
}

export function generateMaintenanceRecord(orderId) {
  return request.post(`/api/maintenance/records/from-order/${orderId}`)
}

export function getMaintenanceReport(id) {
  return request.get(`/api/maintenance/records/${id}/report`)
}
