import request from './request'

export function getMaintenanceRecords(params) {
  return request.get('/api/maintenance/records', { params })
}

export function getMaintenanceRecordDetail(id) {
  return request.get(`/api/maintenance/records/${id}`)
}

export function generateMaintenanceRecordFromOrder(orderId) {
  return request.post(`/api/maintenance/records/from-order/${orderId}`)
}

export function getMaintenanceReport(id) {
  return request.get(`/api/maintenance/records/${id}/report`)
}

export function deleteMaintenanceRecord(id) {
  return request.delete(`/api/maintenance/records/${id}`)
}

export const getMaintenanceRecord = getMaintenanceRecordDetail
export const generateMaintenanceRecord = generateMaintenanceRecordFromOrder
