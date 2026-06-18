import request from './request'

export function getUsers(params) {
  return request.get('/api/users', { params })
}

export function getUserDetail(id) {
  return request.get(`/api/users/${id}`)
}

export function createUser(data) {
  return request.post('/api/users', data)
}

export function updateUser(id, data) {
  return request.put(`/api/users/${id}`, data)
}

export function updateUserRole(id, data) {
  return request.put(`/api/users/${id}/role`, data)
}

export function updateUserStatus(id, data) {
  return request.put(`/api/users/${id}/status`, data)
}

export function resetPassword(id, data) {
  return request.put(`/api/users/${id}/reset-password`, data)
}

export function deleteUser(id) {
  return request.delete(`/api/users/${id}`)
}

export function getRoles() {
  return request.get('/api/users/roles')
}

export function getWorkers() {
  return request.get('/api/users/workers')
}

export function createRole(data) {
  return request.post('/api/users/roles', data)
}

export function updateRole(id, data) {
  return request.put(`/api/users/roles/${id}`, data)
}

export function deleteRole(id) {
  return request.delete(`/api/users/roles/${id}`)
}

export function getMyProfile() {
  return request.get('/api/users/me/profile')
}

export function updateMyProfile(data) {
  return request.put('/api/auth/me', data)
}

export function changeMyPassword(data) {
  return request.put('/api/users/me/password', data)
}
