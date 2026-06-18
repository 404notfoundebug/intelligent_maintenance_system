/**
 * 认证工具模块
 */

const TOKEN_KEY = 'token'
const ROLE_KEY = 'role'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getRole() {
  return localStorage.getItem(ROLE_KEY) || ''
}

export function setRole(role) {
  localStorage.setItem(ROLE_KEY, role)
}

export function removeRole() {
  localStorage.removeItem(ROLE_KEY)
}

export function isLoggedIn() {
  return !!getToken()
}

export function isAdmin() {
  return getRole() === 'admin'
}

export function isWorker() {
  return getRole() === 'worker'
}

/**
 * 根据当前角色获取对应的登录页路径
 */
export function getLoginPath() {
  const role = getRole()
  if (role === 'admin') return '/admin/login'
  if (role === 'worker') return '/worker/login'
  return '/'
}

/**
 * 根据当前角色获取对应的首页路径
 */
export function getDashboardPath() {
  const role = getRole()
  if (role === 'admin') return '/admin/dashboard'
  if (role === 'worker') return '/worker/dashboard'
  return '/'
}

export function clearAuth() {
  removeToken()
  removeRole()
}
