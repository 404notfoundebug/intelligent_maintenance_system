import request from './request'

export function getDashboardSummary() {
  return request.get('/api/dashboard/summary')
}

export function getDeviceStatus() {
  return request.get('/api/dashboard/device-status')
}

export function getFaultStatus() {
  return request.get('/api/dashboard/fault-status')
}

export function getOrderStatus() {
  return request.get('/api/dashboard/order-status')
}

export function getCaseStatus() {
  return request.get('/api/dashboard/case-status')
}

export function getRecentFaults(params) {
  return request.get('/api/dashboard/recent-faults', { params })
}

export function getRecentOrders(params) {
  return request.get('/api/dashboard/recent-orders', { params })
}

export function getRecentMaintenanceRecords(params) {
  return request.get('/api/dashboard/recent-maintenance-records', { params })
}

export function getMonthlyTrend() {
  return request.get('/api/dashboard/monthly-trend')
}
