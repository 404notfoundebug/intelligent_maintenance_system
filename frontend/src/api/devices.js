import request from './request'

export function getDeviceList(params) {
  return request.get('/api/devices', { params })
}

export function getDeviceDetail(id) {
  return request.get(`/api/devices/${id}`)
}

export function createDevice(data) {
  return request.post('/api/devices', data)
}

export function updateDevice(id, data) {
  return request.put(`/api/devices/${id}`, data)
}

export function deleteDevice(id) {
  return request.delete(`/api/devices/${id}`)
}

export const getDevices = getDeviceList
