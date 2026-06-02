import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeStoredUser, removeToken } from '../utils/auth'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000
})

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && payload.code === 200) {
      return payload.data
    }
    const message = payload?.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.response?.data?.detail || '网络或服务异常'
    console.error('API request failed:', {
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      method: error.config?.method,
      status,
      data: error.response?.data,
      message: error.message
    })
    if (status === 401) {
      removeToken()
      removeStoredUser()
      ElMessage.error('登录已失效，请重新登录')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
