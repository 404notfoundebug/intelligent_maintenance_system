import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const role = ref(localStorage.getItem('role') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')
  const isWorker = computed(() => role.value === 'worker')
  const username = computed(() => userInfo.value?.username || '')

  async function login(credentials) {
    // axios 拦截器已经解包：成功时返回 payload.data
    // 即 { access_token, token_type, user: { id, username, role, ... } }
    const data = await loginApi(credentials)
    const user = data.user || {}

    token.value = data.access_token || data.token || ''
    role.value = user.role || data.role || ''
    userInfo.value = user

    localStorage.setItem('token', token.value)
    localStorage.setItem('role', role.value)

    return { role: role.value, token: token.value }
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const res = await getUserInfo()
      // 拦截器已解包，res 直接是 data 对象
      userInfo.value = res || {}
      role.value = userInfo.value?.role || role.value
      localStorage.setItem('role', role.value)
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    role.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  return {
    token,
    userInfo,
    role,
    isLoggedIn,
    isAdmin,
    isWorker,
    username,
    login,
    fetchUserInfo,
    logout
  }
})
