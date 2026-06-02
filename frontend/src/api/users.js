import request from './request'

export function getUsers(params) {
  return request.get('/api/users', { params })
}

export function createUser(data) {
  return request.post('/api/users', data)
}

export function getRoles() {
  return request.get('/api/users/roles')
}

export function getMyProfile() {
  return request.get('/api/users/me/profile')
}

export function changeMyPassword(data) {
  return request.put('/api/users/me/password', data)
}
